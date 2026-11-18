#!/usr/bin/env python3
"""ULMi H1 Sözleşmeden İcraya Köprü™ V1 — doğrulama + salt-okunur görev grafiği.

Mevcut ENGINE/SQLite yürütücüsüne eklenen *giriş adaptörü*, ikinci yürütücü değil.
Bu modül dosya yazmaz, komut çalıştırmaz, ağ çağrısı yapmaz, onay üretmez.
Önceden owner tarafından kabul edilen Pilot A kaynak baytları dış SHA ile kilitlidir.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any

SCHEMA = 'enguru.ulmi.contract-to-execution/v1'
PRODUCT_ID = 'ENGURU_MUHENDIS_OSI'
CONTRACT_ID = 'ULMI-H1-PILOT-A-20261114'
CONTRACT_PIN = '1034b0fc28e9fd4db1530b1564a81958c6469006aa69e1457e2198a089ef39d1'
BASELINE_MANIFEST_PIN = '9ab0785f61eb761db61beac9f2824faf96bde943edd939c55b766e35f89f37e2'
MAX_CONTRACT_BYTES = 12_000
SOURCE_COUNT = 42
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
ARTIFACT = re.compile(r'[A-Za-z0-9_./-]{1,120}\Z')
ID_PREFIX = 'ULMI-A-'


class ContractHold(ValueError):
    """Fail-closed: no execution authority is ever conferred here."""


def _need(condition: bool, error: str) -> None:
    if not condition:
        raise ContractHold(error)


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _object_pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ContractHold('HOLD_DUPLICATE_JSON_KEY')
        result[k] = v
    return result


def _reject_constant(value):
    raise ContractHold('HOLD_NONSTANDARD_JSON_NUMBER')


def _decode_json(raw: bytes):
    try:
        text = raw.decode('utf-8', 'strict')
        return json.loads(text, object_pairs_hook=_object_pairs, parse_constant=_reject_constant)
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, ContractHold):
            raise
        raise ContractHold('HOLD_JSON_INVALID') from exc


def _read_regular(root: Path, relative: str) -> bytes:
    """Reject symlinks from trusted root through leaf; read-only no-follow open."""
    q = PurePosixPath(relative)
    _need(not q.is_absolute() and '..' not in q.parts and '.' not in q.parts
          and '\\' not in relative and str(q) == relative, 'HOLD_SOURCE_PATH')
    target = root
    for component in q.parts:
        target = target / component
        _need(not target.is_symlink(), 'HOLD_SOURCE_SYMLINK')
    _need(target.is_file(), 'HOLD_SOURCE_MISSING')
    try:
        fd = os.open(target, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        with os.fdopen(fd, 'rb') as stream:
            return stream.read(1_000_001)
    except OSError as exc:
        raise ContractHold('HOLD_SOURCE_UNREADABLE') from exc


def verify_baseline(baseline_root: str | Path | None) -> dict:
    """Verify independent original V0.5.7 owner source, NOT this candidate folder."""
    _need(isinstance(baseline_root, (str, Path)) and bool(str(baseline_root)),
          'HOLD_TRUSTED_BASELINE_ROOT_REQUIRED')
    root = Path(baseline_root).expanduser()
    _need(root.is_absolute() and not root.is_symlink() and root.is_dir()
          and root == root.resolve(strict=True), 'HOLD_BASELINE_ROOT')
    manifest_bytes = _read_regular(root, 'KAYNAK_MANIFEST.json')
    _need(_digest(manifest_bytes) == BASELINE_MANIFEST_PIN, 'HOLD_BASELINE_MANIFEST_SHA')
    manifest = _decode_json(manifest_bytes)
    _need(isinstance(manifest, dict) and manifest.get('schema') == 'enguru.muhendis.h1.local-text-source-v1',
          'HOLD_BASELINE_MANIFEST_SCHEMA')
    files = manifest.get('files')
    _need(isinstance(files, dict) and len(files) == SOURCE_COUNT, 'HOLD_BASELINE_FILE_COUNT')
    for rel, expected in files.items():
        _need(isinstance(rel, str) and isinstance(expected, str) and HEX64.fullmatch(expected) is not None,
              'HOLD_BASELINE_MANIFEST_RECORD')
        data = _read_regular(root, 'payload/' + rel)
        _need(_digest(data) == expected, 'HOLD_BASELINE_SOURCE_SHA:' + rel)
    actual = set()
    for p in (root / 'payload').rglob('*'):
        if p.is_file() or p.is_symlink():
            actual.add(p.relative_to(root / 'payload').as_posix())
    _need(actual == set(files), 'HOLD_BASELINE_UNDECLARED_SOURCE')
    return {'manifest_sha256': BASELINE_MANIFEST_PIN, 'verified_files': SOURCE_COUNT,
            'product_id': PRODUCT_ID, 'source_version': '0.5.6+0.5.7-brand',
            'source_role': 'INDEPENDENT_UNMODIFIED_BASELINE'}


def _validate_contract(doc: Any) -> None:
    _need(isinstance(doc, dict), 'HOLD_CONTRACT_OBJECT')
    _need(doc.get('schema') == SCHEMA, 'HOLD_CONTRACT_SCHEMA')
    _need(doc.get('contract_id') == CONTRACT_ID and type(doc.get('revision')) is int
          and doc['revision'] == 1, 'HOLD_CONTRACT_ID_OR_REVISION')
    _need(doc.get('issuer') == 'ChatGPT-produced candidate reviewed by owner', 'HOLD_ISSUER')
    _need(doc.get('owner_design_approval_ref') ==
          'OWNER_ARCHITECTURE_ACCEPTED_20261114_NOT_EXECUTION_AUTHORITY', 'HOLD_DESIGN_APPROVAL_REF')
    _need(doc.get('status') == 'PREPARED_NOT_EXECUTABLE_WITHOUT_SEPARATE_OWNER_GRANT',
          'HOLD_CONTRACT_STATUS')
    _need(doc.get('execution_authorization') is None and
          doc.get('declared_write_scope') == 'OWNER_GRANT_REQUIRED_AT_EXECUTION_NO_ROOT_GRANTED_YET',
          'HOLD_EXECUTION_AUTHORITY')
    signatures = doc.get('signatures')
    _need(isinstance(signatures, dict) and set(signatures) ==
          {'donecheck_signature', 'issuer_signature', 'owner_execution_signature'}
          and all(v is None for v in signatures.values()), 'HOLD_PREMATURE_SIGNATURE')
    project = doc.get('project')
    _need(isinstance(project, dict) and project.get('horizon') == 'H1_ISOLATED_ONLY'
          and project.get('production_install') is False and project.get('public_publish') is False,
          'HOLD_PROJECT_SCOPE')
    baseline = doc.get('technical_baseline')
    _need(isinstance(baseline, dict) and baseline.get('product_id') == PRODUCT_ID
          and baseline.get('core_version') == '0.5.6' and baseline.get('ui_version') == '0.5.7'
          and baseline.get('hash_algorithm') == 'SHA-256'
          and baseline.get('requires_pre_run_readback') is True
          and baseline.get('source_identity') ==
          'PINNED_BY_ULTIMATE_PILOT_SOURCE_MANIFEST_BEFORE_RUN', 'HOLD_TECH_BASELINE')
    budget = doc.get('resource_budget')
    _need(isinstance(budget, dict) and budget.get('external_paid_api') is False
          and budget.get('network') == 'LOOPBACK_ONLY'
          and type(budget.get('wall_seconds_max')) is int and 1 <= budget['wall_seconds_max'] <= 180
          and type(budget.get('memory_mib_max')) is int and 1 <= budget['memory_mib_max'] <= 1024,
          'HOLD_RESOURCE_BUDGET')
    rollback = doc.get('rollback')
    _need(isinstance(rollback, dict) and rollback.get('required') is True
          and rollback.get('pre_change_snapshot_required') is True
          and rollback.get('restore_test_required') is True, 'HOLD_ROLLBACK')
    acceptance = doc.get('acceptance_policy')
    _need(isinstance(acceptance, dict) and acceptance.get('donecheck_signed_reviewer_required') is True
          and acceptance.get('independent_test_oracle') is True
          and acceptance.get('owner_final_acceptance_required') is True, 'HOLD_INDEPENDENT_ACCEPTANCE')
    artifacts = doc.get('allowed_artifacts')
    _need(isinstance(artifacts, list) and len(artifacts) == 4
          and len(set(map(str, artifacts))) == len(artifacts), 'HOLD_ARTIFACT_LIST')
    for path in artifacts:
        _need(isinstance(path, str) and ARTIFACT.fullmatch(path) is not None
              and PurePosixPath(path).as_posix() == path
              and not PurePosixPath(path).is_absolute()
              and '..' not in PurePosixPath(path).parts
              and '\\' not in path and '\x00' not in path,
              'HOLD_ARTIFACT_PATH')
    _need(set(artifacts) == {'index.html', 'app.py', 'tests/test_app.py', 'README.md'},
          'HOLD_UNAPPROVED_ARTIFACT')
    ids = doc.get('required_source_ids')
    _need(isinstance(ids, list) and len(ids) == len(set(map(str, ids))) == 9
          and all(isinstance(v, str) and re.fullmatch(r'H1-C(0[1-9]|1[0-2])', v) for v in ids),
          'HOLD_REQUIRED_ACCEPTANCE_IDS')
    criteria = doc.get('criteria')
    _need(isinstance(criteria, list) and len(criteria) == 8, 'HOLD_CRITERIA_COUNT')
    for i, criterion in enumerate(criteria, 1):
        _need(isinstance(criterion, dict) and criterion.get('id') == f'ULMI-A-{i:02d}'
              and criterion.get('test_ref') == f'ULMI-A-T{i:02d}'
              and criterion.get('required') is True, 'HOLD_CRITERION_TRACEABILITY')


def preview(contract_bytes: bytes, baseline_root: str | Path | None) -> dict:
    """Validates exactly the pinned owner review fixture and builds a non-executable DAG."""
    _need(isinstance(contract_bytes, bytes) and 0 < len(contract_bytes) <= MAX_CONTRACT_BYTES,
          'HOLD_CONTRACT_BYTES')
    observed = _digest(contract_bytes)
    _need(observed == CONTRACT_PIN, 'HOLD_CONTRACT_SHA_MISMATCH')
    doc = _decode_json(contract_bytes)
    _validate_contract(doc)
    baseline = verify_baseline(baseline_root)
    criteria = doc['criteria']
    stages = [
        ('PINNED_CONTRACT', []),
        ('BASELINE_READBACK', ['PINNED_CONTRACT']),
        ('READ_ONLY_DISCOVERY', ['BASELINE_READBACK']),
        ('IMPLEMENTATION_BINDING_REVIEW', ['READ_ONLY_DISCOVERY']),
        ('OWNER_EXECUTION_GATE', ['IMPLEMENTATION_BINDING_REVIEW']),
        ('AUTHORIZED_H1_BUILD', ['OWNER_EXECUTION_GATE']),
        ('FUNCTIONAL_SECURITY_REGRESSION', ['AUTHORIZED_H1_BUILD']),
        ('INDEPENDENT_DONECHECK', ['FUNCTIONAL_SECURITY_REGRESSION']),
        ('OWNER_FINAL_ACCEPTANCE', ['INDEPENDENT_DONECHECK']),
    ]
    nodes = [{'node_id': name, 'depends_on': deps, 'stage': 'PREVIEW_ONLY',
              'execution_allowed': False} for name, deps in stages]
    nodes += [{'node_id': 'TRACE_' + x['id'], 'depends_on': ['IMPLEMENTATION_BINDING_REVIEW'],
               'acceptance_id': x['id'], 'test_id': x['test_ref'],
               'status': 'TRACEABLE_ONLY_NOT_IMPLEMENTATION_BOUND',
               'execution_allowed': False} for x in criteria]
    edges = [[dep, item['node_id']] for item in nodes for dep in item['depends_on']]
    return {
        'schema': 'enguru.ulmi.readonly-contract-graph/v1',
        'status': 'PASS_SCOPED_CONTRACT_VALIDATED_HOLD_EXECUTION',
        'contract_id': CONTRACT_ID, 'revision': 1,
        'contract_sha256': observed, 'baseline': baseline,
        'graph': {'nodes': nodes, 'edges': edges,
                  'sha256': _digest(json.dumps({'nodes':nodes,'edges':edges},
                                               sort_keys=True,separators=(',',':')).encode('utf-8'))},
        'traceability': {'required_acceptance_ids': [x['id'] for x in criteria],
                         'test_refs': [x['test_ref'] for x in criteria],
                         'acceptance_links': '8/8', 'concrete_implementation_bindings': '0/8',
                         'allowed_artifacts': doc['allowed_artifacts'],
                         'missing': 'Owner-reviewed requirements-to-file binding and diff plan'},
        'gates': {'owner_execution': 'HOLD_NO_GRANT',
                  'independent_donecheck': 'NOT_EXECUTED', 'owner_final': 'HOLD',
                  'h1': 'HOLD'},
        'side_effects': 'NONE_THIS_ADAPTER',
        'execution_token': None,
        'next': 'Owner reviews concrete task bindings, then grants separate isolated H1 execution',
    }


def preview_base64(encoded: str, trusted_baseline_root: str | None) -> dict:
    _need(isinstance(encoded, str) and 0 < len(encoded) <= 16_000,
          'HOLD_CONTRACT_TRANSFER')
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ContractHold('HOLD_CONTRACT_BASE64') from exc
    return preview(raw, trusted_baseline_root)
