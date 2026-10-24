#!/usr/bin/env python3
"""ENGÜRÜ Management V6.9 — source-bound live GitHub receipt audit.
Read-only. Authenticated GitHub API observations are NOT DoneCheck/owner grants.
"""
import argparse
import base64
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

REPO = "engurulabory/Engurulaboratuvari"
TASKS = "governance/controller/TASKS.json"
SOURCE = "governance/controller/work/pilot-repair.txt"
WORKFLOW = ".github/workflows/enguru-five-minute-controller.yml"
BOT_LOGIN = "github-actions[bot]"
BOT_ID = 41898282
PROOF_ID = "LABORY_SAFE_REPAIR"
FIELDS = ("id", "action", "path", "expected_sha256", "desired_sha256",
          "replace_from", "replace_to", "dependencies", "target_repo",
          "acceptance_version", "existing_pr_number")
HEX = set("0123456789abcdef")


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def valid_hex(value, length=64):
    return isinstance(value, str) and len(value) == length and not set(value) - HEX


def hold(reason):
    return {"state": "HOLD_GUVENLI_DUR", "reason": reason, "official_finish": "HOLD"}


def evaluate(record, task_ids):
    if not isinstance(record, dict) or record.get("schema") != "enguru.management-v69.operational-observation/v1":
        return hold("SCHEMA")
    if record.get("task_id") not in task_ids: return hold("TASK_ID_UNBOUND")
    if not valid_hex(record.get("source_commit"), 40): return hold("COMMIT_REQUIRED")
    if not all(isinstance(record.get(key), int) and record[key] > 0 for key in
               ("receipt_comment_id", "producer_run_id", "worker_job_id")):
        return hold("RECEIPT_ID_REQUIRED")
    if not all(valid_hex(record.get(key)) for key in ("receipt_full_sha256", "public_receipt_sha256")):
        return hold("INVALID_RECEIPT_DIGEST")
    if any(record.get(k) != v for k, v in
           (("worker_job_conclusion", "success"), ("receipt_state", "PASS"),
            ("receipt_verification", "PASS"))):
        return hold("OBSERVED_EXECUTION_UNPROVEN")
    if any(record.get(k) != v for k, v in
           (("donecheck_state", "HOLD_EXTERNAL_DONECHECK_V1_2"),
            ("official_finish", "HOLD_DONECHECK_HUMAN_GATE"),
            ("task_owner_acceptance", "HOLD"))):
        return hold("FALSE_FINAL_ACCEPTANCE")
    return {"state": "PASS_RECORDED_OPERATION_PROVENANCE_OFFICIAL_HOLD",
            "task_id": record["task_id"], "worker_job_id": record["worker_job_id"],
            "source_commit": record["source_commit"], "receipt_comment_id": record["receipt_comment_id"],
            "source_refresh": "REQUIRED", "live_authentication": "REQUIRED",
            "independent_acceptance": "HOLD", "donecheck": "HOLD",
            "human_threshold": "OWNER_RESERVED", "official_finish": "HOLD"}


def verify_live(record, comment, workflow_run, jobs, tasks, source_bytes, main_sha):
    """Compare independently fetched GitHub objects, never producer flags alone."""
    initial = evaluate(record, {t.get("id") for t in tasks.get("tasks", [])})
    if initial["state"] == "HOLD_GUVENLI_DUR":
        return initial
    if not valid_hex(main_sha, 40) or record["source_commit"] != main_sha:
        return hold("CURRENT_MAIN_SOURCE_DRIFT")
    task = next((t for t in tasks["tasks"] if t.get("id") == record["task_id"]), None)
    if not task or task.get("target_repo") != REPO or task.get("path") != SOURCE:
        return hold("TASK_SCOPE_MISMATCH")
    if sha(source_bytes) != task.get("desired_sha256"):
        return hold("OBSERVED_SOURCE_MISMATCH")
    values = {k: task.get(k) for k in FIELDS}
    values["observed_source_sha256"] = sha(source_bytes)
    values["source_commit"] = main_sha
    fingerprint = sha(canonical(values).encode("utf-8"))
    if not isinstance(comment, dict) or comment.get("id") != record["receipt_comment_id"]:
        return hold("GITHUB_COMMENT_ID")
    user = comment.get("user") or {}
    if user.get("login") != BOT_LOGIN or user.get("id") != BOT_ID:
        return hold("GITHUB_BOT_AUTHOR_MISMATCH")
    if not str(comment.get("issue_url", "")).endswith("/issues/192"):
        return hold("ISSUE_SCOPE_MISMATCH")
    body = comment.get("body") or ""
    marker = re.search(r"<!-- ENGURU_CONTROLLER_V3:(PASS):([^:]+):([0-9a-f]{64}):([0-9]+):([0-9a-f]{40}) -->", body)
    public_sha = re.search(r"(?m)^PUBLIC_RECEIPT_SHA256=([a-f0-9]{64})$", body)
    match = re.search(r"```json\n([^\n]+)\n```", body)
    if not all((marker, public_sha, match)):
        return hold("RECEIPT_FORMAT")
    try:
        public = json.loads(match.group(1))
    except (TypeError, ValueError):
        return hold("RECEIPT_JSON")
    computed_public = sha(canonical(public).encode("utf-8"))
    if computed_public != public_sha.group(1) or computed_public != record["public_receipt_sha256"]:
        return hold("PUBLIC_RECEIPT_SHA256")
    if any((marker.group(2) != record["task_id"],
            marker.group(3) != fingerprint,
            marker.group(4) != str(record["producer_run_id"]),
            marker.group(5) != main_sha,
            public.get("fingerprint") != fingerprint,
            public.get("source_commit") != main_sha,
            public.get("task_id") != record["task_id"],
            str(public.get("producer_run_id")) != str(record["producer_run_id"]),
            public.get("producer_workflow") != WORKFLOW,
            public.get("full_receipt_sha256") != record["receipt_full_sha256"])):
        return hold("FINGERPRINT_OR_SOURCE_PROVENANCE")
    done = public.get("donecheck_producer_candidate") or {}
    verify = public.get("verification") or {}
    if any((public.get("official_verified_finish") != "HOLD_DONECHECK_HUMAN_GATE",
            done.get("doneCheckResult") != "HOLD_EXTERNAL_DONECHECK_V1_2",
            done.get("humanThresholdRequired") is not True,
            done.get("finalState") != "HOLD",
            verify.get("state") != "PASS",
            public.get("engineering", {}).get("state") != "PASS")):
        return hold("RECEIPT_PRODUCER_BOUNDARY")
    if not isinstance(workflow_run, dict) or any((
            workflow_run.get("id") != record["producer_run_id"],
            workflow_run.get("head_sha") != main_sha,
            workflow_run.get("status") != "completed",
            workflow_run.get("conclusion") != "success",
            not str(workflow_run.get("path", "")).split("@")[0].endswith(WORKFLOW),
            workflow_run.get("repository", {}).get("full_name") != REPO)):
        return hold("WORKFLOW_RUN_PROVENANCE")
    if not isinstance(jobs, dict) or not isinstance(jobs.get("jobs"), list):
        return hold("WORKER_JOB_RESPONSE")
    worker = [j for j in jobs["jobs"] if j.get("id") == record["worker_job_id"]]
    if len(worker) != 1 or any((worker[0].get("name") != "worker",
                               worker[0].get("run_id") != record["producer_run_id"],
                               worker[0].get("status") != "completed",
                               worker[0].get("conclusion") != "success")):
        return hold("WORKER_JOB_PROVENANCE")
    return {
        "state": "PASS_GITHUB_PROVENANCE_OFFICIAL_HOLD",
        "task_id": record["task_id"],
        "source_commit": main_sha,
        "verified_source_sha256": sha(source_bytes),
        "verified_task_fingerprint": fingerprint,
        "verified_public_receipt_sha256": computed_public,
        "workflow_run_id": record["producer_run_id"],
        "worker_job_id": record["worker_job_id"],
        "github_bot_identity": "PASS_GITHUB_API_ACCOUNT",
        "receipt_public_integrity": "PASS",
        "worker_observation": "PASS",
        "verifier_claim": "PASS_PRODUCER_ONLY",
        "internal_receipt_integrity": "HOLD_INTERNAL_BYTES_UNAVAILABLE",
        "independent_donecheck": "HOLD",
        "human_threshold": "OWNER_RESERVED",
        "official_finish": "HOLD",
        "next_action": "AUTHENTIC_DONECHECK_V1_2_VERIFICATION_AND_OWNER_DECISION"
    }


def github(path):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise ValueError("GITHUB_TOKEN_READ_AUTH_REQUIRED")
    url = "https://api.github.com/repos/" + REPO + "/" + path
    request = Request(url, headers={"Authorization": "Bearer " + token,
                                    "Accept": "application/vnd.github+json",
                                    "X-GitHub-Api-Version": "2022-11-28",
                                    "User-Agent": "enguru-management-v69-readonly"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def github_source(path, commit):
    import urllib.parse
    doc = github("contents/" + path + "?ref=" + urllib.parse.quote(commit))
    if doc.get("encoding") != "base64":
        raise ValueError("GITHUB_CONTENT_ENCODING")
    return base64.b64decode(doc["content"], validate=False)


def write_once(path, result):
    """Create one no-overwrite evidence report without credentials or signatures."""
    output = Path(path)
    fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--record", default="governance/management-v69/OPERATION_OBSERVATION.json")
    parser.add_argument("--output", help="Write a single immutable JSON evidence projection")
    args = parser.parse_args()
    try:
        path = Path(args.record)
        if path.is_symlink() or not path.is_file():
            raise ValueError("RECORD_FILE")
        record = json.loads(path.read_text(encoding="utf-8"))
        if args.live:
            main_commit = github("commits/main")["sha"]
            task_doc = json.loads(github_source(TASKS, main_commit))
            source_bytes = github_source(SOURCE, main_commit)
            comment = github("issues/comments/" + str(record["receipt_comment_id"]))
            runid = record["producer_run_id"]
            run = github("actions/runs/" + str(runid))
            jobs = github("actions/runs/" + str(runid) + "/jobs?per_page=100")
            result = verify_live(record, comment, run, jobs, task_doc, source_bytes, main_commit)
        else:
            tasks = json.loads(Path(TASKS).read_text(encoding="utf-8"))
            result = evaluate(record, {t["id"] for t in tasks["tasks"]})
    except (OSError, ValueError, KeyError, TypeError, HTTPError, URLError, TimeoutError) as error:
        result = hold("LIVE_READ_OR_SOURCE_ERROR_" + type(error).__name__)
    if args.output:
        try:
            write_once(args.output, result)
        except (OSError, ValueError) as error:
            result = hold("EVIDENCE_OUTPUT_" + type(error).__name__)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result["state"].startswith("PASS_") else 50


if __name__ == "__main__":
    raise SystemExit(main())
