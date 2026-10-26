#!/usr/bin/env python3
"""P06 receipt IO adapter: evidence-root only, exclusive, symlink-safe writes.

Used by existing native and Steward entrypoints. This helper never changes
canonical governance, accepted-candidate state, source, or existing receipts.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import secrets


def _existing_fd(path: Path, evidence_root: Path | None = None):
    """Open only a bounded regular receipt beneath the evidence directory."""
    root = (evidence_root or Path.home()/'Enguru/Evidence/MacEngineer').expanduser()
    dst = Path(path).expanduser()
    if not dst.is_absolute():
        raise ValueError('EVIDENCE_ABSOLUTE_DESTINATION_REQUIRED')
    if '..' in dst.parts or '..' in root.parts:
        raise ValueError('EVIDENCE_PARENT_TRAVERSAL_REJECTED')
    try:
        rel = dst.relative_to(root)
    except ValueError as ex:
        raise ValueError('EVIDENCE_DESTINATION_OUT_OF_SCOPE') from ex
    if len(rel.parts) < 2 or dst.suffix != '.json':
        raise ValueError('EVIDENCE_NAMED_JSON_SUBDIR_REQUIRED')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    opened = [os.open(root, flags)]
    try:
        for component in rel.parts[:-1]:
            opened.append(os.open(component, flags, dir_fd=opened[-1]))
        fd = os.open(rel.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=opened[-1])
        opened.append(fd)
        import stat
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 2_000_000:
            raise ValueError('EVIDENCE_REGULAR_BOUNDED_RECEIPT_REQUIRED')
        return opened
    except BaseException:
        for fd in reversed(opened):
            os.close(fd)
        raise


def read_receipt_json(path: Path, *, evidence_root: Path | None = None) -> dict:
    opened = _existing_fd(path, evidence_root)
    try:
        with os.fdopen(os.dup(opened[-1]), 'rb') as stream:
            data = stream.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError('EVIDENCE_RECEIPT_LIMIT')
        payload = json.loads(data, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        if not isinstance(payload, dict):
            raise ValueError('EVIDENCE_OBJECT_REQUIRED')
        return payload
    finally:
        for fd in reversed(opened):
            os.close(fd)


def write_or_reconcile_json(path: Path, payload: dict, *, evidence_root: Path | None = None) -> Path:
    """Reconcile a publication error only against identical immutable bytes.

    Reconciliation retries file/directory durability. A persistent error remains
    an error; an exception never means that publication had no effect.
    """
    if not isinstance(payload, dict):
        raise ValueError('EVIDENCE_OBJECT_REQUIRED')
    expected = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n').encode('utf-8')
    try:
        return write_new_json(path, payload, evidence_root=evidence_root)
    except OSError as original:
        try:
            opened = _existing_fd(path, evidence_root)
        except (OSError, ValueError):
            raise original
        try:
            with os.fdopen(os.dup(opened[-1]), 'rb') as stream:
                actual = stream.read(2_000_001)
            if actual != expected:
                raise FileExistsError('EVIDENCE_EXISTING_RECEIPT_MISMATCH') from original
            os.fsync(opened[-1])
            for fd in reversed(opened[:-1]):
                os.fsync(fd)
            return Path(path).expanduser()
        finally:
            for fd in reversed(opened):
                os.close(fd)


def write_new_json(path: Path, payload: dict, *, evidence_root: Path | None = None) -> Path:
    if not isinstance(payload, dict):
        raise ValueError('EVIDENCE_OBJECT_REQUIRED')
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    root = (evidence_root or (Path.home() / 'Enguru/Evidence/MacEngineer')).expanduser()
    dst = Path(path).expanduser()
    if not dst.is_absolute():
        raise ValueError('EVIDENCE_ABSOLUTE_DESTINATION_REQUIRED')
    if '..' in dst.parts or '..' in root.parts:
        raise ValueError('EVIDENCE_PARENT_TRAVERSAL_REJECTED')
    if dst.suffix != '.json':
        raise ValueError('EVIDENCE_JSON_SUFFIX_REQUIRED')
    try:
        rel = dst.relative_to(root)
    except ValueError as ex:
        raise ValueError('EVIDENCE_DESTINATION_OUT_OF_SCOPE') from ex
    if len(rel.parts) < 2 or any(p in ('', '.', '..') for p in rel.parts):
        raise ValueError('EVIDENCE_NAMED_SUBDIR_REQUIRED')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    root_fd = os.open(str(root), flags)
    opened = [root_fd]
    temporary = None
    try:
        fd = root_fd
        for component in rel.parts[:-1]:
            try:
                next_fd = os.open(component, flags, dir_fd=fd)
            except FileNotFoundError:
                try:
                    os.mkdir(component, mode=0o700, dir_fd=fd)
                except FileExistsError:
                    pass  # Another creator is checked by O_NOFOLLOW below.
                os.fsync(fd)  # Persist the newly created child directory entry.
                next_fd = os.open(component, flags, dir_fd=fd)
            opened.append(next_fd)
            fd = next_fd
        name = rel.name
        temporary = '.' + name + '.' + secrets.token_hex(9) + '.tmp'
        outfd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        0o600, dir_fd=fd)
        try:
            with os.fdopen(outfd, 'wb') as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            raise
        # Hard-link publishes a complete file atomically, with no replacement.
        os.link(temporary, name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
        os.fsync(fd)  # Publish the completed receipt durably before cleanup.
        os.unlink(temporary, dir_fd=fd)
        os.fsync(fd)
        temporary = None
        return dst
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary, dir_fd=opened[-1])
            except FileNotFoundError:
                pass
        for fd in reversed(opened):
            os.close(fd)
