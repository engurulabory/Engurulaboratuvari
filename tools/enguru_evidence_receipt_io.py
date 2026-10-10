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


def write_new_json(path: Path, payload: dict, *, evidence_root: Path | None = None) -> Path:
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
                os.mkdir(component, mode=0o700, dir_fd=fd)
                next_fd = os.open(component, flags, dir_fd=fd)
            opened.append(next_fd)
            fd = next_fd
        name = rel.name
        encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
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
        os.unlink(temporary, dir_fd=fd)
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
