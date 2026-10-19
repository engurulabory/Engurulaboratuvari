"""Read-only Python import dependency inventory for the existing v2.4 test terminal.
No module execution or implicit authority.
"""
import ast
import json
from pathlib import Path

def inventory(root, test_names):
    root=Path(root).resolve()
    records={}
    missing=[]
    for test in test_names:
        name="tests/"+test
        p=root/name
        if p.is_symlink() or not p.is_file():
            missing.append({"source":name,"reason":"MISSING_OR_SYMLINK"})
            continue
        try:
            tree=ast.parse(p.read_text(encoding="utf-8"),filename=name)
        except (OSError,UnicodeError,SyntaxError):
            missing.append({"source":name,"reason":"SOURCE_PARSE_FAILURE"})
            continue
        imports=sorted({n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module})
        imports+=sorted({a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names})
        local={}
        for mod in sorted(set(imports)):
            if mod=="tools" or mod.startswith("tools."):
                parts=mod.split(".")
                target=root.joinpath(*parts).with_suffix(".py")
                alt=root.joinpath(*parts,"__init__.py")
                if (target.is_file() and not target.is_symlink()):
                    local[mod]=str(target.relative_to(root))
                elif (alt.is_file() and not alt.is_symlink()):
                    local[mod]=str(alt.relative_to(root))
                else:
                    missing.append({"source":name,"module":mod,"reason":"LOCAL_IMPORT_UNRESOLVED"})
        records[name]=local
    return {"schema":"enguru.suzgec.v24.test-import-inventory/v1","scope":"DIRECT_STATIC_IMPORTS_ONLY","tests":records,"blockers":missing,"state":"PASS_DIRECT_IMPORTS_RESOLVED" if not missing else "HOLD_GUVENLI_DUR","transitiveRuntimeDependencies":"HOLD_NOT_ANALYZED","verifiedFinish":"HOLD"}
