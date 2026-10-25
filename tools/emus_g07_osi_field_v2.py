#!/usr/bin/env python3
"""EMUS G07 V2: local read-only model identity, loaded memory, functional probe."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
from urllib.request import Request, urlopen
from datetime import datetime, timezone


def get(path, timeout=10):
    with urlopen("http://127.0.0.1:11434" + path, timeout=timeout) as res:
        return json.loads(res.read())


def measure(model, probe=False):
    record = {"schema": "enguru.emus.g07.field-v2", "at": datetime.now(timezone.utc).isoformat(),
              "requested_model": model, "platform": platform.system(),
              "authority": "FIELD_EVIDENCE_ONLY"}
    if record["platform"] != "Darwin":
        record["state"] = "HOLD_MAC_REQUIRED"
        return record
    try:
        tags = get("/api/tags")
        matches = [m for m in tags.get("models", []) if m.get("name") == model or m.get("model") == model]
        if len(matches) != 1 or not matches[0].get("digest"):
            record["state"] = "HOLD_EXACT_MODEL_IDENTITY"
            return record
        item = matches[0]
        record["model"] = {"name": item.get("name"), "digest": item["digest"],
                           "size_bytes": item.get("size"), "details": item.get("details")}
        record["loaded_before"] = get("/api/ps").get("models", [])
        record["vm_before"] = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout[:4500]
        if probe:
            body = json.dumps({"model": model, "stream": False, "think": False,
                "messages": [{"role": "system", "content": "Respond with ONLY the exact user-requested token. No punctuation or reasoning."},
                             {"role": "user", "content": "EMUS_G07_LOCAL_PASS"}],
                "options": {"num_predict": 48, "temperature": 0}}).encode()
            start = time.monotonic()
            with urlopen(Request("http://127.0.0.1:11434/api/chat", data=body,
                         headers={"Content-Type": "application/json"}, method="POST"), timeout=120) as res:
                answer = json.loads(res.read())
            output = str(answer.get("message", {}).get("content", "")).strip()
            record["probe"] = {"elapsed_s": round(time.monotonic()-start, 3),
                               "response_match": output == "EMUS_G07_LOCAL_PASS",
                               "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
                               "eval_count": answer.get("eval_count"),
                               "eval_duration_ns": answer.get("eval_duration"),
                               "total_duration_ns": answer.get("total_duration")}
        record["loaded_after"] = get("/api/ps").get("models", [])
        record["vm_after"] = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout[:4500]
        record["state"] = "FIELD_COLLECTED_ACCEPTANCE_PENDING"
    except Exception as error:
        record["state"] = "HOLD_FIELD_QUERY"
        record["error_type"] = type(error).__name__
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3:14b")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    result = measure(args.model, args.probe)
    if result["state"] == "HOLD_MAC_REQUIRED":
        print("STATE=HOLD_MAC_REQUIRED")
        return 3
    target = args.output.expanduser()
    if target.exists() or target.is_symlink():
        print("STATE=HOLD_OUTPUT_EXISTS")
        return 2
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode()
    with target.open("xb") as stream:
        stream.write(raw)
    print("STATE="+result["state"])
    print("EVIDENCE="+str(target))
    print("SHA256="+hashlib.sha256(raw).hexdigest())
    return 0 if result["state"] == "FIELD_COLLECTED_ACCEPTANCE_PENDING" else 4


if __name__ == "__main__":
    raise SystemExit(main())
