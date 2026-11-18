"""ENGÜRÜ Mühendis OSi H1: sürümlü ve dar yetkili yerleşik yetenek kayıt noktası.

Yalnızca gözden geçirilmiş, bu kaynak paketiyle dağıtılan modüller kaydedilir.
Dışarıdan dosya/plugin yükleme veya dinamik komut çalıştırma yoktur.
"""
from __future__ import annotations
import ast
import hashlib
import os
from pathlib import Path
from typing import Any

CAPABILITY = {
    'id': 'PY_DIAGNOSTIC_V1',
    'version': '1.0.0',
    'title': 'Python sözdizimi teşhisi',
    'permissions': ['READ_OWN_INPUT', 'CREATE_ONE_NEW_MD_IN_WORKSPACE'],
    'network': 'NONE',
    'shell': 'NONE',
    'kind': 'BUILTIN_REVIEWED_MODULE',
    'scope': 'STATIK_AST_DIAGNOSIS_NOT_GENERAL_CODE_REPAIR',
}

def module_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def enabled() -> bool:
    return os.environ.get('ENGURU_H1_DISABLE_PY_DIAGNOSTIC', '0') != '1'

def registry() -> list[dict[str, Any]]:
    return [{**CAPABILITY, 'enabled': enabled(), 'source_sha256': module_sha256()}]

def _validated_source(source: str) -> str:
    if not isinstance(source, str) or not 4 <= len(source.strip()) <= 4000:
        raise ValueError('Teşhis girdisi 4–4000 karakter olmalı.')
    if '\x00' in source:
        raise ValueError('Kod metninde NUL karakteri olamaz.')
    return source

def diagnostic(source: str) -> dict[str, Any]:
    """Source is *only parsed*; never exec/import/eval or shell."""
    source = _validated_source(source)
    code_hash = hashlib.sha256(source.encode('utf-8')).hexdigest()
    try:
        tree = ast.parse(source)
        functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        return {'syntax': 'PASS', 'functions': functions, 'line': None,
                'detail': 'Python AST sözdizimi geçerli. Davranış ve kalite ayrıca test edilir.',
                'source_sha256': code_hash, 'line_count':len(source.splitlines())}
    except SyntaxError as err:
        return {'syntax': 'DIAGNOSED_SYNTAX_ERROR', 'functions': None,
                'line': err.lineno, 'detail': str(err.msg)[:160],
                'source_sha256': code_hash, 'line_count':len(source.splitlines())}

def render(source: str) -> str:
    result = diagnostic(source)
    return ('# ENGÜRÜ Mühendis OSi™ — Python Statik Teşhis Makbuzu\n\n'
            'Modül: `PY_DIAGNOSTIC_V1` · Sürüm: `1.0.0`\n\n'
            f"- Kaynak SHA-256: `{result['source_sha256']}`\n"
            f"- Modül kaynak SHA-256: `{module_sha256()}`\n"
            f"- Kaynak satırları: {result['line_count']}\n"
            f"- Sözdizimi durumu: `{result['syntax']}`\n"
            f"- Teşhis satırı: {result['line'] if result['line'] is not None else 'yok'}\n"
            f"- Tanımlı fonksiyon: {result['functions'] if result['functions'] is not None else 'değerlendirilmedi'}\n"
            f"- Açıklama: {result['detail']}\n\n"
            '## Yeterlilik sınırı\n'
            'Yalnız Python AST ayrıştırması yapıldı; kod çalıştırılmadı. '
            'Davranış testi, otomatik kod onarımı, bağımsız DoneCheck ve ürün kabulü bu makbuzla ilan edilmez.\n')
