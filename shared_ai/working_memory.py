from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

from shared_ai.harvest_controls import EvidenceGatedSkillLearning


SCHEMA_VERSION = "1.0"
TASK_STATES = frozenset({"ACTIVE", "HOLD", "BLOCKED", "PASS"})
LEARNING_STATES = frozenset(
    {"OBSERVED", "LEARNING_CANDIDATE", "EVIDENCE", "FRESH_REVIEW", "ACCEPTED", "REJECTED", "PROMOTED"}
)
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,120}$")


class WorkingMemoryError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_refs(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(v).strip() for v in values if str(v).strip()))


@dataclass(frozen=True)
class DurableTaskRecord:
    task_id: str
    objective: str
    authority_snapshot: dict[str, Any]
    required_capabilities: tuple[str, ...]
    revision: int = 1
    state: str = "ACTIVE"
    transitions: tuple[dict[str, Any], ...] = tuple()
    artifact_refs: tuple[str, ...] = tuple()
    evidence_refs: tuple[str, ...] = tuple()
    human_decisions: tuple[dict[str, Any], ...] = tuple()
    resume_checkpoint: dict[str, Any] | None = None
    final_outcome: dict[str, Any] | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_dict(cls, p: dict[str, Any]) -> "DurableTaskRecord":
        return cls(
            task_id=str(p["task_id"]),
            objective=str(p["objective"]),
            authority_snapshot=dict(p.get("authority_snapshot", {})),
            required_capabilities=tuple(str(x) for x in p.get("required_capabilities", [])),
            revision=int(p.get("revision", 1)),
            state=str(p.get("state", "ACTIVE")).upper(),
            transitions=tuple(dict(x) for x in p.get("transitions", [])),
            artifact_refs=tuple(str(x) for x in p.get("artifact_refs", [])),
            evidence_refs=tuple(str(x) for x in p.get("evidence_refs", [])),
            human_decisions=tuple(dict(x) for x in p.get("human_decisions", [])),
            resume_checkpoint=dict(p["resume_checkpoint"]) if p.get("resume_checkpoint") else None,
            final_outcome=dict(p["final_outcome"]) if p.get("final_outcome") else None,
            created_at=str(p.get("created_at", _now())),
            updated_at=str(p.get("updated_at", _now())),
            schema_version=str(p.get("schema_version", SCHEMA_VERSION)),
        )


@dataclass(frozen=True)
class LearningRecord:
    learning_id: str
    producer_id: str
    observation_count: int
    state: str = "OBSERVED"
    evidence_refs: tuple[str, ...] = tuple()
    benchmark_pass: bool = False
    reviewer_id: str | None = None
    review_evidence: tuple[str, ...] = tuple()
    decision_reason: str = ""
    promoted_version: str | None = None
    promoted_target: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_dict(cls, p: dict[str, Any]) -> "LearningRecord":
        return cls(
            learning_id=str(p["learning_id"]),
            producer_id=str(p["producer_id"]),
            observation_count=int(p["observation_count"]),
            state=str(p.get("state", "OBSERVED")).upper(),
            evidence_refs=tuple(str(x) for x in p.get("evidence_refs", [])),
            benchmark_pass=bool(p.get("benchmark_pass", False)),
            reviewer_id=str(p["reviewer_id"]) if p.get("reviewer_id") else None,
            review_evidence=tuple(str(x) for x in p.get("review_evidence", [])),
            decision_reason=str(p.get("decision_reason", "")),
            promoted_version=str(p["promoted_version"]) if p.get("promoted_version") else None,
            promoted_target=str(p["promoted_target"]) if p.get("promoted_target") else None,
            created_at=str(p.get("created_at", _now())),
            updated_at=str(p.get("updated_at", _now())),
            schema_version=str(p.get("schema_version", SCHEMA_VERSION)),
        )


class _JsonStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @staticmethod
    def _id(value: str, label: str) -> str:
        value = str(value).strip()
        if not _SAFE_ID.fullmatch(value):
            raise WorkingMemoryError(f"invalid_{label}")
        return value

    @staticmethod
    def _read(path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise WorkingMemoryError("record_not_found") from exc
        if not isinstance(payload, dict):
            raise WorkingMemoryError("invalid_record_payload")
        return payload

    @staticmethod
    def _write(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


class PersistentWorkingMemory(_JsonStore):
    """File-backed Task State + Evidence extension. Runtime path is caller-owned."""

    def _task_path(self, task_id: str) -> Path:
        return self.root / "tasks" / f"{self._id(task_id, 'task_id')}.json"

    def create_task(
        self,
        *,
        task_id: str,
        objective: str,
        authority_snapshot: dict[str, Any],
        required_capabilities: tuple[str, ...],
    ) -> DurableTaskRecord:
        task_id = self._id(task_id, "task_id")
        if not objective.strip():
            raise WorkingMemoryError("objective_required")
        if not authority_snapshot:
            raise WorkingMemoryError("authority_snapshot_required")
        capabilities = _clean_refs(required_capabilities)
        if not capabilities:
            raise WorkingMemoryError("required_capabilities_required")
        path = self._task_path(task_id)
        if path.exists():
            raise WorkingMemoryError("task_already_exists")
        now = _now()
        record = DurableTaskRecord(
            task_id=task_id,
            objective=objective.strip(),
            authority_snapshot=dict(authority_snapshot),
            required_capabilities=capabilities,
            transitions=({"from": None, "to": "ACTIVE", "reason": "task_created", "at": now},),
            created_at=now,
            updated_at=now,
        )
        self._write(path, asdict(record))
        return record

    def load_task(self, task_id: str) -> DurableTaskRecord:
        record = DurableTaskRecord.from_dict(self._read(self._task_path(task_id)))
        if record.schema_version != SCHEMA_VERSION:
            raise WorkingMemoryError("unsupported_task_schema")
        if record.state not in TASK_STATES:
            raise WorkingMemoryError("invalid_task_state")
        return record

    def update_task(
        self,
        task_id: str,
        *,
        expected_revision: int,
        state: str | None = None,
        reason: str = "",
        artifact_refs: tuple[str, ...] = tuple(),
        evidence_refs: tuple[str, ...] = tuple(),
        human_decision: dict[str, str] | None = None,
        checkpoint: dict[str, Any] | None = None,
        final_summary: str | None = None,
    ) -> DurableTaskRecord:
        current = self.load_task(task_id)
        if current.revision != expected_revision:
            raise WorkingMemoryError("stale_task_revision")
        target = current.state if state is None else str(state).upper()
        if target not in TASK_STATES:
            raise WorkingMemoryError("invalid_task_state")
        if target != current.state and not reason.strip():
            raise WorkingMemoryError("transition_reason_required")

        merged_evidence = _clean_refs((*current.evidence_refs, *evidence_refs))
        merged_artifacts = _clean_refs((*current.artifact_refs, *artifact_refs))
        decisions = current.human_decisions
        if human_decision is not None:
            required = {"decision", "authority", "evidence_ref"}
            if not required.issubset(human_decision) or not all(str(human_decision[k]).strip() for k in required):
                raise WorkingMemoryError("human_decision_evidence_required")
            entry = {**human_decision, "at": _now()}
            decisions = (*decisions, entry)
            merged_evidence = _clean_refs((*merged_evidence, str(human_decision["evidence_ref"])))

        next_checkpoint = current.resume_checkpoint
        if checkpoint is not None:
            checkpoint_id = self._id(str(checkpoint.get("checkpoint_id", "")), "checkpoint_id")
            summary = str(checkpoint.get("summary", "")).strip()
            next_action = str(checkpoint.get("next_action", "")).strip()
            if not summary or not next_action:
                raise WorkingMemoryError("checkpoint_summary_and_next_action_required")
            cp_evidence = _clean_refs(tuple(str(x) for x in checkpoint.get("evidence_refs", [])))
            merged_evidence = _clean_refs((*merged_evidence, *cp_evidence))
            next_checkpoint = {
                "checkpoint_id": checkpoint_id,
                "task_revision": current.revision + 1,
                "state": target,
                "summary": summary,
                "next_action": next_action,
                "evidence_refs": list(cp_evidence),
                "at": _now(),
            }

        transitions = current.transitions
        if target != current.state:
            transitions = (
                *transitions,
                {"from": current.state, "to": target, "reason": reason.strip(), "at": _now()},
            )

        final_outcome = current.final_outcome
        if final_summary is not None:
            if not final_summary.strip():
                raise WorkingMemoryError("final_summary_required")
            if target == "PASS" and not merged_evidence:
                raise WorkingMemoryError("pass_requires_evidence")
            final_outcome = {
                "verdict": target,
                "summary": final_summary.strip(),
                "evidence_refs": list(merged_evidence),
                "at": _now(),
            }

        updated = replace(
            current,
            revision=current.revision + 1,
            state=target,
            transitions=transitions,
            artifact_refs=merged_artifacts,
            evidence_refs=merged_evidence,
            human_decisions=decisions,
            resume_checkpoint=next_checkpoint,
            final_outcome=final_outcome,
            updated_at=_now(),
        )
        self._write(self._task_path(task_id), asdict(updated))
        return updated

    def resume_task(self, task_id: str, *, checkpoint_id: str) -> DurableTaskRecord:
        record = self.load_task(task_id)
        checkpoint = record.resume_checkpoint
        if not checkpoint:
            raise WorkingMemoryError("resume_checkpoint_required")
        if checkpoint.get("checkpoint_id") != checkpoint_id:
            raise WorkingMemoryError("resume_checkpoint_mismatch")
        if record.state == "PASS" and record.final_outcome:
            raise WorkingMemoryError("task_already_verified_finish")
        return record


class GovernedLearningPromotion(_JsonStore):
    """OBSERVED -> candidate -> evidence -> fresh review -> accept/reject -> versioned promotion."""

    def _path(self, learning_id: str) -> Path:
        return self.root / "learning" / f"{self._id(learning_id, 'learning_id')}.json"

    def create(self, *, learning_id: str, producer_id: str, observation_count: int = 1) -> LearningRecord:
        learning_id = self._id(learning_id, "learning_id")
        producer_id = self._id(producer_id, "producer_id")
        if observation_count < 1:
            raise WorkingMemoryError("observation_count_required")
        path = self._path(learning_id)
        if path.exists():
            raise WorkingMemoryError("learning_already_exists")
        record = LearningRecord(learning_id, producer_id, observation_count)
        self._write(path, asdict(record))
        return record

    def load(self, learning_id: str) -> LearningRecord:
        record = LearningRecord.from_dict(self._read(self._path(learning_id)))
        if record.schema_version != SCHEMA_VERSION or record.state not in LEARNING_STATES:
            raise WorkingMemoryError("invalid_learning_record")
        return record

    def _save(self, record: LearningRecord) -> LearningRecord:
        record = replace(record, updated_at=_now())
        self._write(self._path(record.learning_id), asdict(record))
        return record

    def to_candidate(self, learning_id: str) -> LearningRecord:
        current = self.load(learning_id)
        if current.state != "OBSERVED":
            raise WorkingMemoryError("learning_state_requires_observed")
        if current.observation_count < 3:
            raise WorkingMemoryError("repeated_observation_required")
        return self._save(replace(current, state="LEARNING_CANDIDATE"))

    def attach_evidence(
        self, learning_id: str, *, evidence_refs: tuple[str, ...], benchmark_pass: bool
    ) -> LearningRecord:
        current = self.load(learning_id)
        if current.state != "LEARNING_CANDIDATE":
            raise WorkingMemoryError("learning_state_requires_candidate")
        evidence_refs = _clean_refs(evidence_refs)
        if not evidence_refs:
            raise WorkingMemoryError("learning_evidence_required")
        if not benchmark_pass:
            raise WorkingMemoryError("learning_benchmark_required")
        return self._save(
            replace(current, state="EVIDENCE", evidence_refs=evidence_refs, benchmark_pass=True)
        )

    def fresh_review(
        self, learning_id: str, *, reviewer_id: str, review_evidence: tuple[str, ...]
    ) -> LearningRecord:
        current = self.load(learning_id)
        if current.state != "EVIDENCE":
            raise WorkingMemoryError("learning_state_requires_evidence")
        reviewer_id = self._id(reviewer_id, "reviewer_id")
        if reviewer_id == current.producer_id:
            raise WorkingMemoryError("fresh_review_requires_independence")
        review_evidence = _clean_refs(review_evidence)
        if not review_evidence:
            raise WorkingMemoryError("fresh_review_evidence_required")
        return self._save(
            replace(
                current,
                state="FRESH_REVIEW",
                reviewer_id=reviewer_id,
                review_evidence=review_evidence,
            )
        )

    def decide(
        self,
        learning_id: str,
        *,
        decision: str,
        reason: str,
        human_approved: bool = False,
    ) -> LearningRecord:
        current = self.load(learning_id)
        if current.state != "FRESH_REVIEW":
            raise WorkingMemoryError("learning_state_requires_fresh_review")
        decision = str(decision).upper()
        if decision not in {"ACCEPT", "REJECT"} or not reason.strip():
            raise WorkingMemoryError("valid_learning_decision_required")
        if decision == "ACCEPT":
            gate = EvidenceGatedSkillLearning().assess(
                observation_count=current.observation_count,
                evidence=current.evidence_refs,
                benchmark_pass=current.benchmark_pass,
                human_approved=human_approved,
            )
            if gate.state != "PASS":
                raise WorkingMemoryError(gate.reason)
            return self._save(replace(current, state="ACCEPTED", decision_reason=reason.strip()))
        return self._save(replace(current, state="REJECTED", decision_reason=reason.strip()))

    def promote(self, learning_id: str, *, version: str, target: str) -> LearningRecord:
        current = self.load(learning_id)
        if current.state != "ACCEPTED":
            raise WorkingMemoryError("learning_state_requires_accept")
        if not version.strip() or not target.strip():
            raise WorkingMemoryError("version_and_target_required")
        return self._save(
            replace(
                current,
                state="PROMOTED",
                promoted_version=version.strip(),
                promoted_target=target.strip(),
            )
        )
