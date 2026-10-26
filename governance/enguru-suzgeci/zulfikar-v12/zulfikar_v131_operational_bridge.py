#!/usr/bin/env python3
"""Zulfikar v1.3.1: read-only mission -> existing Mac Engineer registry preflight.

The bridge checks SOURCE, TASK, ACTION, AUTHORITY and RECOVERY without
running any action. It does not create a new executor, core, issuer or writer.
Real tasks are delegated only to their existing authorized operator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

SCHEMA = "enguru.zulfikar.operational-preflight/v1.3.1"
ROOT = Path(__file__).resolve().parents[3]
BINDING_PATH = "governance/mac-engineer/CAPABILITY_EXECUTION_BINDING_V1.json"
ACTION_PATH = "governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json"
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_hash(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def read_no_symlink(root: Path, relative: str, limit: int) -> bytes:
    """Read a regular file through O_NOFOLLOW directory fds, bounded and fstat checked.

    This proves one file's captured bytes, not multi-file snapshot atomicity.
    """
    p=Path(relative)
    if p.is_absolute() or not p.parts or any(x in (".","..") for x in p.parts):
        raise ValueError("UNSAFE_RELATIVE_PATH")
    root_abs=root.absolute()
    if any(part.is_symlink() for part in (root_abs, *root_abs.parents)):
        raise ValueError("SYMLINKED_ROOT")
    flags=os.O_RDONLY | getattr(os,"O_DIRECTORY",0) | getattr(os,"O_NOFOLLOW",0)
    fd=os.open(root_abs,flags)
    try:
        for part in p.parts[:-1]:
            nextfd=os.open(part,flags,dir_fd=fd)
            os.close(fd)
            fd=nextfd
        leaf=os.open(p.parts[-1],os.O_RDONLY | getattr(os,"O_NOFOLLOW",0) |
                     getattr(os,"O_NONBLOCK",0),dir_fd=fd)
        with os.fdopen(leaf,"rb") as stream:
            before=os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size>limit:
                raise ValueError("FILE_NOT_REGULAR_OR_OVERSIZE")
            data=stream.read(limit+1)
            after=os.fstat(stream.fileno())
            if (len(data)>limit or
                 (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
                 != (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)):
                raise ValueError("FILE_CHANGED_DURING_READ")
            return data
    finally:
        os.close(fd)


def source_read(root: Path, relative: str):
    """Source SHA must match immutable, tracked checkout HEAD bytes exactly."""
    local=read_no_symlink(root,relative,2_000_000)
    before=head_sha(root)
    cmd=subprocess.run(["git","-C",str(root),"show",before+":"+relative],
                       capture_output=True,timeout=12,check=False)
    after=head_sha(root)
    if cmd.returncode or before!=after or cmd.stdout!=local:
        raise ValueError("REGISTRY_SOURCE_DRIFT")
    return json.loads(local.decode("utf-8")), hashlib.sha256(local).hexdigest()


def head_sha(root: Path):
    cmd=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],capture_output=True,timeout=12)
    value=cmd.stdout.decode().strip()
    if cmd.returncode or not SHA.fullmatch(value):
        raise ValueError("UNVERIFIED_HEAD")
    return value


def text_id(value):
    return isinstance(value,str) and ID.fullmatch(value) is not None


def ordered_errors(mission, binding, actions, actual_head):
    """Never promote a claim in mission data to an execution fact."""
    failures=[]
    if not isinstance(mission,dict):
        return ["HOLD_INVALID_MISSION"]
    if mission.get("schema")!=SCHEMA:
        failures.append("HOLD_SCHEMA")
    for key in ("missionId","projectId","workId","capabilityId","actionId","writerId"):
        if not text_id(mission.get(key)):
            failures.append("HOLD_ID_"+key.upper())
    if mission.get("ownerId")!="engurulabory" or mission.get("issuer")!="EXISTING_CANONICAL_ONLY":
        failures.append("HOLD_OWNER_ISSUER")
    if mission.get("sourceHead")!=actual_head:
        failures.append("HOLD_EXACT_HEAD")
    dependencies=mission.get("dependencies")
    if not isinstance(dependencies,list) or any(not isinstance(x,dict) or
            not text_id(x.get("workId")) or x.get("state")!="PASS_EVIDENCED" or
            not isinstance(x.get("receiptSha256"),str) or not SHA256.fullmatch(x["receiptSha256"])
            for x in dependencies):
        failures.append("HOLD_DEPENDENCY_EVIDENCE")
    elif len({x["workId"] for x in dependencies})!=len(dependencies) or any(x["workId"]==mission.get("workId") for x in dependencies):
        failures.append("HOLD_DEPENDENCY_COLLISION")
    if isinstance(dependencies,list) and dependencies:
        # SHA-shaped strings alone are claims; unverified external receipts do
        # not establish dependency completion.
        failures.append("HOLD_DEPENDENCY_PROVENANCE_REVIEW_REQUIRED")
    if mission.get("singleWriter") is not True or mission.get("writerCount")!=1 or type(mission.get("writerCount")) is not int:
        failures.append("HOLD_SINGLE_WRITER")
    if mission.get("remotePushRequested") is not False:
        failures.append("HOLD_REMOTE_PUSH")
    if mission.get("dryRunOnly") is not True:
        failures.append("HOLD_REQUIRES_DRY_RUN")
    if mission.get("humanThreshold")!="HOLD" or mission.get("officialFinish")!="HOLD":
        failures.append("HOLD_PREMATURE_AUTHORITY")
    if mission.get("checkpointState") not in ("NEW","RESUME_PROPOSED"):
        failures.append("HOLD_CHECKPOINT_STATE")
    if mission.get("checkpointState")=="RESUME_PROPOSED":
        # No proof was provided from an authorized durable writer.
        failures.append("HOLD_RESUME_PROOF_REQUIRED")
    records=binding.get("bindings") if isinstance(binding,dict) else None
    mapping=actions.get("actions") if isinstance(actions,dict) else None
    if not isinstance(records,list) or not isinstance(mapping,dict):
        failures.append("HOLD_REGISTRY_FORMAT")
    else:
        matches=[x for x in records if isinstance(x,dict) and x.get("CAPABILITY_ID")==mission.get("capabilityId")]
        if len(matches)!=1:
            failures.append("HOLD_CAPABILITY_IDENTITY")
        else:
            b=matches[0]
            if b.get("BINDING_TYPE")!="REGISTERED_ACTION" or b.get("ACTION")!=mission.get("actionId"):
                failures.append("HOLD_UNBOUND_OR_MISMATCHED_ACTION")
            requested_action=mission.get("actionId")
            action=mapping.get(requested_action) if text_id(requested_action) else None
            if not isinstance(action,dict) or not action.get("handler") or \
                    action.get("handler")!=b.get("REGISTERED_HANDLER") or \
                    action.get("authority")!=b.get("AUTHORITY"):
                failures.append("HOLD_ACTION_HANDLER_AUTHORITY")
            if b.get("EXECUTION_AUTHORITY_CREATED") is not False:
                failures.append("HOLD_AUTHORITY_EXPANSION")
            if mission.get("networkRequested") is not False and (
                 mission.get("networkRequested") is not True or b.get("NETWORK_ALLOWED") is not True):
                failures.append("HOLD_NETWORK_SCOPE")
            # Such actions need actual scoped Human Threshold, which this
            # read-only bridge can never produce.
            if b.get("HUMAN_THRESHOLD_REQUIRED") is True or \
                    str(b.get("AUTHORITY","")).startswith(("RED_","AMBER_HT")):
                failures.append("HOLD_ACTION_REQUIRES_HUMAN_THRESHOLD")
    return sorted(set(failures))


def assess(mission, binding, actions, actual_head, registry_hashes):
    checks=ordered_errors(mission,binding,actions,actual_head)
    valid=isinstance(mission,dict)
    mid=mission.get("missionId") if valid and text_id(mission.get("missionId")) else "UNKNOWN"
    source=mission.get("sourceHead") if valid and SHA.fullmatch(str(mission.get("sourceHead",""))) else None
    reply={
      "schema":"enguru.zulfikar.operational-decision/v1.3.1",
      "missionId":mid,"missionHash":canonical_hash(mission) if valid else None,
      "sourceHead":source,"actualCheckoutHead":actual_head,
      "registrySourceSha256":registry_hashes,
      "decision":"HOLD" if checks else "PREFLIGHT_READY_EXISTING_OPERATOR_ONLY",
      "holds":checks,
      "registeredAction":mission.get("actionId") if valid and not checks else None,
      "realTaskExecuted":False,
      "newCoreCreated":False,"newActionCreated":False,"newIssuerCreated":False,
      "sourceWrites":0,"remotePushes":0,
      "checkpointPersisted":False,"actualUserBenefit":"NOT_MEASURED",
      "ownerIdentityAuthenticated":False, "singleWriterLockObserved":False,
      "actualHandlerInvoked":False, "realWorkIdExistsInCanonicalSource":"NOT_CHECKED",
      "manifestClaimsAreNotAuthorization":True,
      "independentExternalBenchmark":"NOT_RUN",
      "osiRuntime":"HOLD_NOT_OBSERVED",
      "officialVerifiedFinish":"HOLD",
      "nextAction":"Route to existing authorized Mac Engineer runtime for real task and evidence" if not checks
           else "Reconcile holds and obtain exact source/authority evidence"
    }
    return reply


def main(argv=None):
    p=argparse.ArgumentParser(description="Read-only verified Zulfikar mission preflight")
    p.add_argument("command",choices=("preflight",))
    p.add_argument("--input",required=True,help="Manifest JSON file; read-only")
    ns=p.parse_args(argv)
    try:
        path=Path(ns.input).absolute()
        mission=json.loads(read_no_symlink(path.parent,path.name,120000).decode("utf-8"))
        head=head_sha(ROOT)
        binding,bhash=source_read(ROOT,BINDING_PATH)
        actions,ahash=source_read(ROOT,ACTION_PATH)
        if head_sha(ROOT)!=head:
            raise ValueError("MULTI_FILE_HEAD_DRIFT")
        result=assess(mission,binding,actions,head,{BINDING_PATH:bhash,ACTION_PATH:ahash})
        ret=0 if not result["holds"] else 2
    except (ValueError,OSError,UnicodeError,subprocess.TimeoutExpired,TypeError):
        result={"schema":"enguru.zulfikar.operational-decision/v1.3.1",
                "decision":"HOLD","holds":["HOLD_INPUT_OR_SOURCE_READ"],
                "realTaskExecuted":False,"officialVerifiedFinish":"HOLD"}
        ret=2
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return ret


if __name__=="__main__":
    raise SystemExit(main())
