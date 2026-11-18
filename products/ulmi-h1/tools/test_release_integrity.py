#!/usr/bin/env python3
"""Positive, negative and regression acceptance of source-only H1 packaging."""
import importlib.util
import io
import json
import tempfile
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('build_release', Path(__file__).with_name('build_release.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory(prefix='ulmi-h1-release-') as tmp:
    root = Path(tmp)
    (root/'PRODUCT').mkdir()
    (root/'TESTS').mkdir()
    (root/'PRODUCT/index.html').write_bytes(b'<!doctype html><title>ULMi</title>')
    (root/'TESTS/test_a.py').write_bytes(b'assert True\n')
    first, rows, manifest = module.make(root)
    assert module.verify(first)['files']
    print('PASS clean_source_manifest')

    (root/'PRODUCT/__pycache__').mkdir()
    (root/'PRODUCT/__pycache__/app.cpython-313.pyc').write_bytes(b'fake-pyc-may-vary')
    (root/'PRODUCT/app.pyc').write_bytes(b'another-compiled-copy')
    second, _, _ = module.make(root)
    assert first == second
    print('PASS generated_bytecode_cannot_change_zip')

    (root/'PRODUCT/index.html').write_bytes(b'<!doctype html><title>ULMi v2</title>')
    third, _, _ = module.make(root)
    assert first != third and module.verify(third)['files']
    print('PASS source_change_changes_zip')

    (root/'outside.secret').write_bytes(b'NEVER-ARCHIVE-THIS')
    (root/'PRODUCT/private-link.txt').symlink_to(root/'outside.secret')
    try:
        module.make(root)
    except ValueError as e:
        assert str(e).startswith('HOLD_RELEASE_SYMLINK:')
    else:
        raise AssertionError('symlink accepted by packager')
    print('PASS symlink_rejected')

    (root/'PRODUCT/private-link.txt').unlink()
    untampered, _, _ = module.make(root)
    with zipfile.ZipFile(io.BytesIO(untampered)) as src:
        items = {name: src.read(name) for name in src.namelist()}
    items['ULMI_H1/PRODUCT/index.html'] = b'tampered-output'
    changed = io.BytesIO()
    with zipfile.ZipFile(changed,'w',compression=zipfile.ZIP_DEFLATED) as out:
        for name, content in items.items(): out.writestr(name,content)
    try:
        module.verify(changed.getvalue())
    except ValueError as e:
        assert str(e).startswith('HOLD_RELEASE_SHA_DRIFT:')
    else:
        raise AssertionError('tampered ZIP accepted')
    print('PASS manipulated_zip_rejected')
print('RELEASE_INTEGRITY=5/5 PASS_SCOPED')
