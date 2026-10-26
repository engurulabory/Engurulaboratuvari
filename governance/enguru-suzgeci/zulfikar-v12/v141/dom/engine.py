"""ENGURU Dongu Onarim (DOM) V1.0 — pre-GitHub proof-of-operation.

Stage-based, goal-bound, bounded iterative coordinator, NOT a new owner,
remote executor, signing authority or official DoneCheck implementation.
Only an external existing authorized executor can supply callbacks in production.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import copy
import hashlib
import json
import os
import stat
import fcntl
from contextlib import contextmanager

GATES = ("T01", "T02", "A01", "A02", "A03", "A04", "A05", "A06")
MAX_ROUNDS = 12


def canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class Contract:
    goal_id: str
    goal_text: str
    stage: str
    criteria: tuple[str, ...]
    source_pin: str
    scope: str = "LOCAL_DISPOSABLE_PROOF"

    def validate(self):
        if (not isinstance(self.goal_id, str) or not self.goal_id.strip() or
            not isinstance(self.goal_text, str) or not self.goal_text.strip() or
            self.stage not in GATES or not isinstance(self.criteria, tuple) or
            len(self.criteria) == 0 or len(self.criteria) != len(set(self.criteria)) or
            any(not isinstance(c, str) or not c.strip() for c in self.criteria) or
            not isinstance(self.source_pin, str) or len(self.source_pin) != 64 or
            any(c not in "0123456789abcdef" for c in self.source_pin) or
            self.scope != "LOCAL_DISPOSABLE_PROOF"):
            raise ValueError("INVALID_OR_UNAUTHORIZED_CONTRACT")

    def record(self):
        self.validate()
        return {"goalId": self.goal_id, "goalText": self.goal_text,
                "stage": self.stage, "criteria": list(self.criteria),
                "sourcePin": self.source_pin, "scope": self.scope}


def assess(criterion_results, required):
    if (not isinstance(criterion_results, dict) or
        set(criterion_results) != set(required) or
        any(type(v) is not bool for v in criterion_results.values())):
        raise ValueError("INVALID_ASSESSMENT_OR_MISSING_CRITERIA")
    # Diagnostic only, never a user-visible accepted score.
    return (sum(criterion_results.values()) * 100) // len(required)


class LocalJournal:
    """Private disposable journal: chained records, OS writer lock and fd-safe I/O.

    Hash chaining detects accidental modifications against a separately pinned
    head. It does NOT authenticate a human issuer or prevent malicious rewriting.
    """
    MAX_BYTES = 4_000_000

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        if self.folder.is_symlink() or not self.folder.is_dir():
            raise ValueError("UNSAFE_JOURNAL_DIRECTORY")
        self.path = self.folder / "dom-events.jsonl"
        self.lock_path = self.folder / ".dom-writer.lock"
        self._writer_active = False
        self.events = self.read()

    def _open_regular(self, path, flags, mode=0o600):
        fd = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0), mode)
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                raise ValueError("UNSAFE_JOURNAL_LINK_OR_TYPE")
            resolved = os.stat(path, follow_symlinks=False)
            if (st.st_dev, st.st_ino) != (resolved.st_dev, resolved.st_ino):
                raise ValueError("JOURNAL_PATH_CHANGED_DURING_OPEN")
            return fd
        except BaseException:
            os.close(fd)
            raise

    def read(self):
        if not self.path.exists() and not self.path.is_symlink():
            return []
        fd = self._open_regular(self.path, os.O_RDONLY)
        try:
            parts = []
            size = 0
            while True:
                chunk = os.read(fd, 64 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > self.MAX_BYTES:
                    raise ValueError("JOURNAL_TOO_LARGE")
                parts.append(chunk)
            data = b"".join(parts)
        finally:
            os.close(fd)
        if data and not data.endswith(b"\n"):
            raise ValueError("INCOMPLETE_JOURNAL_RECORD")
        rows = data.splitlines()
        prior = "0" * 64
        events = []
        for idx, row in enumerate(rows, 1):
            entry = json.loads(row)
            if not isinstance(entry, dict) or set(entry) != {"number", "prior", "payload", "hash"}:
                raise ValueError("NONCANONICAL_JOURNAL_RECORD")
            payload = entry["payload"]
            expected = sha({"number": idx, "prior": prior, "payload": payload})
            if type(entry.get("number")) is not int or entry["number"] != idx or entry["prior"] != prior or entry["hash"] != expected:
                raise ValueError("JOURNAL_CHAIN_TAMPERED")
            events.append(entry)
            prior = expected
        return events

    @contextmanager
    def writer(self):
        if self._writer_active:
            raise ValueError("REENTRANT_WRITER_FORBIDDEN")
        fd = self._open_regular(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as err:
                raise ValueError("CONCURRENT_WRITER_BLOCKED") from err
            if self.read() != self.events:
                raise ValueError("MULTI_WRITER_OR_JOURNAL_DRIFT")
            self._writer_active = True
            try:
                yield
            finally:
                self._writer_active = False
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def append(self, payload):
        if not self._writer_active:
            with self.writer():
                return self._append_locked(payload)
        return self._append_locked(payload)

    def _append_locked(self, payload):
        if self.read() != self.events:
            raise ValueError("MULTI_WRITER_OR_JOURNAL_DRIFT")
        idx = len(self.events) + 1
        prior = self.events[-1]["hash"] if self.events else "0" * 64
        entry = {"number": idx, "prior": prior, "payload": copy.deepcopy(payload)}
        entry["hash"] = sha(entry)
        line = canonical_bytes(entry) + b"\n"
        fd = self._open_regular(self.path, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
        try:
            wrote = os.write(fd, line)
            if wrote != len(line):
                raise ValueError("SHORT_JOURNAL_WRITE")
            os.fsync(fd)
        finally:
            os.close(fd)
        directory_fd = os.open(self.folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        self.events.append(entry)
        return entry["hash"]


def actual_source_digest(path: Path):
    """Read a regular single-link source without following symlinks."""
    p = Path(path)
    fd = os.open(p, os.O_RDONLY | getattr(os,"O_NOFOLLOW",0))
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or st.st_size>2_000_000:
            raise ValueError("UNSAFE_SOURCE_FILE")
        content=[]
        n=0
        while True:
            chunk=os.read(fd, 65536)
            if not chunk: break
            n+=len(chunk)
            if n>2_000_000: raise ValueError("SOURCE_TOO_LARGE")
            content.append(chunk)
        return hashlib.sha256(b"".join(content)).hexdigest()
    finally:
        os.close(fd)


def pin_artifact_snapshot(journal, artifact_path, expected):
    """Commit evidence is a separate pinned byte snapshot, not a live pathname.

    This is integrity/durability within the existing cooperative single writer;
    it does not grant OS isolation against a privileged arbitrary writer.
    """
    if not isinstance(artifact_path, str) or not Path(artifact_path).is_absolute():
        raise ValueError("ACTUAL_ARTIFACT_PATH_REQUIRED")
    if actual_source_digest(Path(artifact_path)) != expected:
        raise ValueError("LIVE_ARTIFACT_DIGEST_MISMATCH")
    fd = journal._open_regular(Path(artifact_path), os.O_RDONLY)
    try:
        parts = []
        size = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            size += len(chunk)
            if size > 2_000_000:
                raise ValueError("ARTIFACT_SNAPSHOT_TOO_LARGE")
            parts.append(chunk)
        data = b"".join(parts)
    finally:
        os.close(fd)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("ARTIFACT_CHANGED_WHILE_SNAPSHOTTING")
    name = "dom-artifact-" + expected + ".bin"
    target = journal.folder / name
    try:
        fd = journal._open_regular(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        if actual_source_digest(target) != expected:
            raise ValueError("ARTIFACT_SNAPSHOT_DRIFT")
    else:
        try:
            offset = 0
            while offset < len(data):
                wrote = os.write(fd, data[offset:])
                if wrote <= 0:
                    raise ValueError("ARTIFACT_SNAPSHOT_SHORT_WRITE")
                offset += wrote
            os.fchmod(fd, 0o400)
            os.fsync(fd)
        finally:
            os.close(fd)
        directory_fd = os.open(journal.folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    return name


def artifact_checkpoint_current(journal, run, snapshot_name):
    expected = run.get("artifactSha256")
    return (snapshot_name == "dom-artifact-" + str(expected) + ".bin" and
            actual_source_digest(journal.folder / snapshot_name) == expected and
            actual_source_digest(Path(run["artifactPath"])) == expected)


def stop(reason, rounds, contract_hash=None, journal_hash=None):
    return {"state": "AWAIT_REPAIR_OR_AUTHORIZED_EVIDENCE", "reason": reason,
            "contractSha256": contract_hash, "journalHeadSha256": journal_hash,
            "rounds": rounds, "acceptedScore": None, "stagePassIssued": False,
            "productVerifiedFinish": "NOT_ISSUED", "executorAuthorityCreated": False}


def execute(contract: Contract, start_state: dict, journal: LocalJournal,
            simulator: Callable, evaluator: Callable, repairer: Callable,
            real_tester: Callable, independent_verifier: Callable,
            source_probe: Callable, max_rounds: int = 3,
            source_file: Path | None = None, predecessor_receipt: dict | None = None,
            predecessor_verifier: Callable | None = None):
    """Run a local rehearsal using callbacks; never promote to official stage PASS.

    Production execution requires separate scoped owner-approved Work/Mac Engineer
    adapters. Return is at most a 100/100 candidate for independent stage review.
    """
    try:
        contract.validate()
        if (not isinstance(start_state, dict) or type(max_rounds) is not int or
            max_rounds < 1 or max_rounds > MAX_ROUNDS or
            not all(callable(x) for x in (simulator, evaluator, repairer, real_tester, independent_verifier, source_probe))):
            raise ValueError("INVALID_ENGINE_INPUT")
        c = contract.record()
        pinned = sha(c)
        if source_file is None:
            return stop("SOURCE_FILE_REQUIRED", [], pinned)
        if contract.stage != GATES[0]:
            predecessor = GATES[GATES.index(contract.stage) - 1]
            if (not isinstance(predecessor_receipt, dict) or
                predecessor_receipt.get("stage") != predecessor or
                predecessor_receipt.get("goalId") != contract.goal_id or
                predecessor_receipt.get("acceptedScore") != 100 or
                predecessor_receipt.get("authorizedScope") is not True or
                not callable(predecessor_verifier) or
                predecessor_verifier(copy.deepcopy(predecessor_receipt), copy.deepcopy(c)) is not True):
                return stop("PREVIOUS_GATE_AUTHORIZED_ACCEPTANCE_REQUIRED", [], pinned)
        with journal.writer():
            return _execute_inside_writer(contract, start_state, journal, simulator, evaluator,
                repairer, real_tester, independent_verifier, source_probe, max_rounds,
                c, pinned, source_file)
    except (ValueError, TypeError, KeyError, OSError, OverflowError, RecursionError) as exc:
        return stop("SAFE_FAILURE_" + type(exc).__name__, [], None)


def _execute_inside_writer(contract, start_state, journal, simulator, evaluator,
                           repairer, real_tester, independent_verifier, source_probe,
                           max_rounds, c, pinned, source_file):
    try:
        previous = journal.events[-1]["payload"] if journal.events else None
        if previous and previous.get("contractSha256") != pinned:
            return stop("CONTRACT_SWITCH_FORBIDDEN", [], pinned)
        if actual_source_digest(Path(source_file)) != contract.source_pin:
            return stop("ACTUAL_SOURCE_DIGEST_MISMATCH", [], pinned)
        if source_probe(copy.deepcopy(c)) is not True:
            return stop("LIVE_SOURCE_PIN_MISMATCH", [], pinned)
        if previous and previous.get("stateSha256") != sha(start_state):
            return stop("RESUME_STATE_DIFFERS_FROM_VERIFIED_CHECKPOINT", [], pinned)
        # A verified 100 checkpoint is idempotent and may only be promoted by
        # external stage authority. No repeat repairs or task execution.
        if previous and previous.get("afterDiagnostic") == 100:
            # Idempotency skips task execution, not current evidence validation.
            # Recheck persisted output through the existing separate verifier.
            history = previous.get("executionProof")
            if (not isinstance(history, dict) or history.get("processObserved") is not True or
                type(history.get("exitCode")) is not int or history["exitCode"] != 0 or
                history.get("artifactSha256") != previous.get("artifactSha256") or
                history.get("scope") != contract.scope or
                not isinstance(history.get("artifactPath"), str)):
                return stop("CHECKPOINT_PROCESS_PROOF_REQUIRED", [], pinned)
            # Revalidation observes bytes now; it does not observe a new task process.
            replay_run = {"processObserved": False, "exitCode": None,
                "executionMode": "CHECKPOINT_REVALIDATION_NO_NEW_TASK_PROCESS",
                "replayedProcessProof": copy.deepcopy(history),
                "scope": contract.scope, "artifactSha256": previous.get("artifactSha256"),
                "artifactPath": history["artifactPath"]}
            if (assess(evaluator(copy.deepcopy(start_state), copy.deepcopy(c)), contract.criteria) != 100 or
                independent_verifier(copy.deepcopy(start_state), copy.deepcopy(c),
                                     copy.deepcopy(replay_run)) is not True):
                return stop("REPLAY_ARTIFACT_OR_CRITERIA_CHANGED", [], pinned)
            if (actual_source_digest(Path(source_file)) != contract.source_pin or
                source_probe(copy.deepcopy(c)) is not True):
                return stop("SOURCE_CHANGED_DURING_REPLAY_VERIFY", [], pinned)
            if journal.read() != journal.events:
                return stop("JOURNAL_CHANGED_DURING_REPLAY_VERIFY", [], pinned)
            if not artifact_checkpoint_current(journal, replay_run, previous.get("artifactSnapshot")):
                return stop("REPLAY_ARTIFACT_OR_SNAPSHOT_CHANGED", [], pinned)
            return {"state": "STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED",
                    "contractSha256": pinned, "journalHeadSha256": journal.events[-1]["hash"],
                    "diagnostic": 100, "rounds": [], "acceptedScore": None,
                    "stagePassIssued": False, "productVerifiedFinish": "NOT_ISSUED",
                    "executorAuthorityCreated": False, "replayedVerifiedCheckpoint": True,
                    "processObserved": False, "executionMode": "CHECKPOINT_REVALIDATION_NO_NEW_TASK_PROCESS",
                    "previousExecutionProof": copy.deepcopy(history)}
        # Resume is caller-supplied, reconciled to the prior checkpoint hash.
        state = copy.deepcopy(start_state)
        rounds = []
        verified_prior: set[str] = set()
        for index in range(max_rounds):
            if actual_source_digest(Path(source_file)) != contract.source_pin or source_probe(copy.deepcopy(c)) is not True:
                return stop("LIVE_SOURCE_PIN_MISMATCH", rounds, pinned)
            if sha(contract.record()) != pinned:
                return stop("GOAL_DRIFT", rounds, pinned)
            sim_before = simulator(copy.deepcopy(state), c)
            if not isinstance(sim_before, dict) or sim_before.get("valid") is not True:
                return stop("SIMULATION_REJECTED", rounds, pinned)
            before = evaluator(copy.deepcopy(state), c)
            old = assess(before, contract.criteria)
            accepted_before = {k for k, v in before.items() if v}
            if not verified_prior.issubset(accepted_before):
                return stop("PROVEN_GAIN_REGRESSION", rounds, pinned)
            missing = [key for key in contract.criteria if not before[key]]
            record = {"iteration": index + 1, "initialDiagnostic": old,
                      "gaps": missing, "simulated": True, "realTestVerified": False}
            candidate = repairer(copy.deepcopy(state), tuple(missing), c) if missing else copy.deepcopy(state)
            if not isinstance(candidate, dict) or (missing and candidate == state):
                return stop("REPAIR_INVALID_OR_NO_PROGRESS", rounds + [record], pinned)
            run = real_tester(copy.deepcopy(candidate), c)
            if (not isinstance(run, dict) or run.get("processObserved") is not True or
                type(run.get("exitCode")) is not int or run["exitCode"] != 0 or
                run.get("scope") != "LOCAL_DISPOSABLE_PROOF" or
                not isinstance(run.get("artifactSha256"), str) or len(run["artifactSha256"]) != 64 or
                not isinstance(run.get("artifactPath"), str) or
                independent_verifier(copy.deepcopy(candidate), c, copy.deepcopy(run)) is not True):
                return stop("REAL_TEST_OR_INDEPENDENT_VERIFY_FAILED", rounds + [record], pinned)
            record["realTestVerified"] = True
            if actual_source_digest(Path(source_file)) != contract.source_pin or source_probe(copy.deepcopy(c)) is not True:
                return stop("SOURCE_CHANGED_DURING_REAL_TEST", rounds + [record], pinned)
            sim_after = simulator(copy.deepcopy(candidate), c)
            if not isinstance(sim_after, dict) or sim_after.get("valid") is not True:
                return stop("RESIMULATION_REJECTED", rounds + [record], pinned)
            after = evaluator(copy.deepcopy(candidate), c)
            current_score = assess(after, contract.criteria)
            now = {k for k, v in after.items() if v}
            if not accepted_before.issubset(now) or current_score < old:
                return stop("REPAIR_CAUSED_REGRESSION", rounds + [record], pinned)
            record.update({"afterDiagnostic": current_score, "remaining": [k for k in contract.criteria if not after[k]],
                           "artifactSha256": run["artifactSha256"], "sourcePin": contract.source_pin,
                           "contractSha256": pinned, "gate": contract.stage})
            if actual_source_digest(Path(source_file)) != contract.source_pin or source_probe(copy.deepcopy(c)) is not True:
                return stop("SOURCE_CHANGED_BEFORE_CHECKPOINT", rounds + [record], pinned)
            # Simulation/assessment callbacks may have touched the artifact after
            # its initial verification. Revalidate before recording a checkpoint.
            if independent_verifier(copy.deepcopy(candidate), copy.deepcopy(c), copy.deepcopy(run)) is not True:
                return stop("ARTIFACT_CHANGED_BEFORE_CHECKPOINT", rounds + [record], pinned)
            if actual_source_digest(Path(source_file)) != contract.source_pin or source_probe(copy.deepcopy(c)) is not True:
                return stop("SOURCE_CHANGED_BEFORE_CHECKPOINT", rounds + [record], pinned)
            snapshot = pin_artifact_snapshot(journal, run["artifactPath"], run["artifactSha256"])
            execution_proof = {key: copy.deepcopy(run[key]) for key in
                ("processObserved", "exitCode", "scope", "artifactSha256", "artifactPath")}
            journal_head = journal.append({"contractSha256": pinned, "gate": contract.stage,
                "iteration": index + 1, "afterDiagnostic": current_score, "artifactSha256": run["artifactSha256"],
                "scope": contract.scope, "stateSha256": sha(candidate), "externalAuthority": False,
                "artifactSnapshot": snapshot, "executionProof": execution_proof})
            # Detect a writer changing the live output during journal publication.
            # The pinned snapshot remains auditable even when the current output drifts.
            if not artifact_checkpoint_current(journal, run, snapshot):
                return stop("ARTIFACT_CHANGED_AT_CHECKPOINT", rounds + [record], pinned, journal_head)
            rounds.append(record)
            state = copy.deepcopy(candidate)
            verified_prior = now
            if current_score == 100:
                if actual_source_digest(Path(source_file)) != contract.source_pin or source_probe(copy.deepcopy(c)) is not True:
                    return stop("SOURCE_CHANGED_DURING_REAL_TEST", rounds, pinned, journal_head)
                if not artifact_checkpoint_current(journal, run, snapshot):
                    return stop("ARTIFACT_CHANGED_AT_CHECKPOINT", rounds, pinned, journal_head)
                return {"state": "STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED",
                        "contractSha256": pinned, "journalHeadSha256": journal_head,
                        "diagnostic": 100, "rounds": rounds, "acceptedScore": None,
                        "stagePassIssued": False, "productVerifiedFinish": "NOT_ISSUED",
                        "executorAuthorityCreated": False}
        return stop("BOUNDED_CYCLE_CONTINUE", rounds, pinned,
                    journal.events[-1]["hash"] if journal.events else None)
    except (ValueError, TypeError, KeyError, OSError, OverflowError, RecursionError) as exc:
        return stop("SAFE_FAILURE_" + type(exc).__name__, [], None)


def audit_real_work_handoff(contract: Contract, workspace: Path,
                            acceptance_requirements: dict, evidence_bindings: list,
                            phase_runs: list, *, observed_working_result: bool = False,
                            independent_review: dict | None = None,
                            owner_decision: dict | None = None,
                            donecheck: dict | None = None,
                            existing_authority_verifier=None, completion_attestation=None,
                            independent_session_verifier=None):
    """V1.4.1 DÖM handoff audit within the existing engine.

    Keeps local evidence, executed-task proofs, and official decisions distinct.
    It never runs Work, writes to GitHub, issues owner decisions or claims PASS.
    """
    from proof_chain import audit_evidence, assess_three_phase_runs, finish_readiness
    from completion_guard import audit_completion_claim
    contract.validate()
    # Missing or malformed evidence requirements must return an actionable HOLD,
    # never a crash (especially when a model has omitted the contract entirely).
    try:
        evidence = audit_evidence(workspace, acceptance_requirements,
                                  evidence_bindings, goal_id=contract.goal_id)
    except (ValueError, TypeError, OSError):
        evidence = {'state': 'EVIDENCE_HOLD', 'goalId': contract.goal_id,
                    'criteriaTotal': len(contract.criteria), 'criteriaMet': 0,
                    'invalid': [{'reason': 'ACCEPTANCE_REQUIREMENTS_OR_BINDINGS_INVALID'}],
                    'acceptedScore': None, 'officialPassIssued': False}
    # Supplied evidence criteria must be the exact original acceptance scope.
    # A narrowed/substituted acceptance contract cannot produce a ready handoff.
    if not isinstance(acceptance_requirements, dict) or set(acceptance_requirements) != set(contract.criteria):
        evidence['state'] = 'EVIDENCE_HOLD'
        evidence['originalCriteriaMismatch'] = {
            'missing': sorted(set(contract.criteria) - set(acceptance_requirements or {}) if isinstance(acceptance_requirements, dict) else set(contract.criteria)),
            'extra': sorted(set(acceptance_requirements or {}) - set(contract.criteria)) if isinstance(acceptance_requirements, dict) else []
        }
    phases = assess_three_phase_runs(workspace, phase_runs, goal_id=contract.goal_id)
    completion = audit_completion_claim(workspace, contract, completion_attestation,
        independent_session_verifier=independent_session_verifier)
    finish = finish_readiness(contract.goal_id, evidence, phases,
        observed_working_result=observed_working_result,
        independent_review=independent_review, owner_decision=owner_decision,
        donecheck=donecheck, existing_authority_verifier=existing_authority_verifier)
    if completion['state'] != 'CROSS_SESSION_LOCAL_COMPLETENESS_CANDIDATE':
        finish = {'state':'FINISH_HOLD','missing':sorted(set(
            finish.get('missing', []) + ['CROSS_SESSION_COMPLETENESS_PROOF'])),
            'acceptedScore':None,'verifiedFinishIssued':False}
    return {'goalId': contract.goal_id, 'stage': contract.stage,
            'contractSha256': sha(contract.record()),
            'evidence': evidence, 'realExecution': phases, 'completion': completion,
            'finish': finish,
            'stagePassIssued': False, 'productVerifiedFinish': 'NOT_ISSUED',
            'nextAction': ('EXTERNAL_OWNER_DONECHECK_VERIFY' if
              completion['state'] == 'CROSS_SESSION_LOCAL_COMPLETENESS_CANDIDATE' and
              evidence['state'] == 'EVIDENCE_READY_FOR_EXTERNAL_REVIEW' and
              phases['state'] == 'THREE_PHASE_LOCAL_PROOF_CANDIDATE' and
              observed_working_result is True and
              set(finish.get('missing', [])) <= {'INDEPENDENT_REVIEW_RECORD', 'OWNER_DECISION_RECORD',
                      'OFFICIAL_DONECHECK_RECORD', 'EXISTING_AUTHORITY_BRIDGE', 'AUTHORIZED_ACCEPTANCE_UNVERIFIED'}
              else 'REPAIR_MISSING_REAL_EVIDENCE')}
