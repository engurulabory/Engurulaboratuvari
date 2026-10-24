#!/usr/bin/env python3
"""EMUS G07 read-only Mac OSi model and resource field evidence collector.

Collects existing local Ollama state and one small opt-in inference. Never
downloads or installs a model, modifies Ollama configuration or claims acceptance.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
import urllib.request


def command(*args: str, timeout: int = 20) -> dict:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return {"exit_code": p.returncode, "stdout": p.stdout[:10000], "stderr": p.stderr[:1000]}
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return {"state": "HOLD", "reason": type(exc).__name__}


def inspect(model: str, *, run_inference: bool = False) -> dict:
    result = {
        "schema": "enguru.emus.g07.osi.field-evidence/v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(),
        "requested_model": model,
        "mode": "READ_ONLY_LOCAL_NO_INSTALL",
    }
    if platform.system() != "Darwin":
        result["state"] = "HOLD_MAC_OSI_REQUIRED"
        return result
    result["ollama_version"] = command("ollama", "--version")
    result["models"] = command("ollama", "list")
    result["model_details"] = command("ollama", "show", model, "--json")
    result["loaded_models"] = command("ollama", "ps")
    result["system_memory"] = command("sysctl", "-n", "hw.memsize")
    result["vm_stat_before"] = command("vm_stat")
    usage = shutil.disk_usage(Path.home())
    result["disk"] = {"total_bytes": usage.total, "used_bytes": usage.used, "free_bytes": usage.free}
    result["license_source"] = "INSTALLED_MODEL_METADATA_ONLY"
    if run_inference and result["model_details"].get("exit_code") == 0:
        # Explicit local loopback and a fixed minimal prompt, never secrets.
        payload = json.dumps({
            "model": model,
            "prompt": "Reply with exactly EMUS_G07_LOCAL_PASS",
            "stream": False,
            "options": {"num_predict": 24},
        }).encode("utf-8")
        started = time.monotonic()
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                raw = json.loads(response.read())
            result["inference"] = {
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "model": raw.get("model"),
                "response_match": raw.get("response", "").strip() == "EMUS_G07_LOCAL_PASS",
                "eval_count": raw.get("eval_count"),
                "eval_duration_ns": raw.get("eval_duration"),
                "load_duration_ns": raw.get("load_duration"),
                "total_duration_ns": raw.get("total_duration"),
            }
        except Exception as exc:
            result["inference"] = {"state": "HOLD", "reason": type(exc).__name__}
        result["vm_stat_after"] = command("vm_stat")
    result["state"] = "FIELD_EVIDENCE_COLLECTED_NOT_ACCEPTED"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3:14b")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inference", action="store_true")
    args = parser.parse_args()
    # Keep outputs in user's chosen archival location.
    target = args.output.expanduser()
    if target.exists() or target.is_symlink():
        print("STATE=HOLD_OUTPUT_EXISTS")
        return 2
    result = inspect(args.model, run_inference=args.inference)
    if result["state"] == "HOLD_MAC_OSI_REQUIRED":
        print("STATE=HOLD_MAC_OSI_REQUIRED")
        return 3
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    with target.open("xb") as fh:
        fh.write(raw)
    print("STATE=" + result["state"])
    print("EVIDENCE=" + str(target))
    print("SHA256=" + hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
