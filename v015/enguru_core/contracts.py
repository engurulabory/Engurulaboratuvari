"""Immutable typed contracts. Model strings are data, never capabilities."""
from dataclasses import dataclass, asdict
import hashlib
import json


class Rejected(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_json(raw):
    if not isinstance(raw, str) or len(raw.encode()) > 100000:
        raise Rejected('JSON_SIZE_OR_TYPE')
    def pairs(items):
        d = {}
        for k,v in items:
            if k in d: raise Rejected('DUPLICATE_KEY')
            d[k] = v
        return d
    def constant(_): raise Rejected('NONFINITE')
    try: return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, TypeError, RecursionError) as e: raise Rejected('INVALID_JSON') from e


@dataclass(frozen=True)
class Plan:
    task: str
    version: str
    source: str
    scope: str
    blocks: tuple

    def validate(self):
        if any(not isinstance(x, str) or not x for x in (self.task,self.version,self.source,self.scope)):
            raise Rejected('PLAN_IDENTITY')
        if len(self.source)!=64 or any(c not in '0123456789abcdef' for c in self.source):
            raise Rejected('SOURCE_DIGEST')
        ids=[b[0] for b in self.blocks]
        if not ids or len(ids)!=len(set(ids)): raise Rejected('BLOCK_IDS')
        if any(type(b[1]) is not int or b[1]<=0 for b in self.blocks) or sum(b[1] for b in self.blocks)!=10000:
            raise Rejected('WEIGHTS_10000')
        deps={b[0]:b[2] for b in self.blocks};seen=set();active=set()
        def visit(k):
            if k in active: raise Rejected('DAG_CYCLE')
            if k in seen:return
            if k not in deps:raise Rejected('UNKNOWN_DEPENDENCY')
            active.add(k)
            for dep in deps[k]:visit(dep)
            active.remove(k);seen.add(k)
        for k in ids:visit(k)
        return self

    @property
    def sha(self):
        self.validate()
        return digest(asdict(self))


def remaining(done):
    if type(done) is not int or not 0<=done<=100: raise Rejected('PERCENT_RANGE')
    return 100-done


def progress(plan, verified):
    plan.validate(); weights={b[0]:b[1] for b in plan.blocks}
    if len(verified)!=len(set(verified)) or any(k not in weights for k in verified):
        raise Rejected('UNKNOWN_OR_DUPLICATE_BLOCK')
    done=sum(weights[k] for k in verified)
    return {'done_weight':done,'total_weight':10000,'completion_percent':done/100,
            'remaining_percent':(10000-done)/100}


def repair_gate(history):
    if len(history)>=3:raise Rejected('THREE_ROUND_LIMIT')
    if len(history)>=2 and history[-1]==history[-2]:raise Rejected('NEW_DIAGNOSIS_REQUIRED')
    return True
