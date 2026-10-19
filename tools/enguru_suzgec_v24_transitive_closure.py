"""Read-only, bounded AST dependency closure for the 19-file Süzgeç Twin candidate.

Evaluates local tools/tests imports transitively; rejects unresolved third-party and
dynamic imports. Does not execute imported code or confer native authority.
"""
import ast
import json
import sys
from pathlib import Path, PurePosixPath

def assess(root, names):
    root=Path(root).resolve(strict=True)
    findings=[]
    checked={}
    active=set()
    def issue(src, reason, detail=""):
        findings.append({"source":src,"reason":reason,"detail":detail})
    def visit(name):
        if name in checked or name in active: return
        rel=PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix()!=name or not name.endswith(".py"):
            issue(name,"UNSAFE_SOURCE");return
        target=root.joinpath(*rel.parts)
        if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
            issue(name,"SOURCE_MISSING_OR_UNSAFE");return
        active.add(name)
        try:
            tree=ast.parse(target.read_text(encoding="utf-8"),filename=name)
        except (OSError,UnicodeError,SyntaxError) as exc:
            issue(name,"PARSE_FAILURE",type(exc).__name__)
            active.remove(name);return
        deps=set()
        for node in ast.walk(tree):
            mods=[]
            if isinstance(node,ast.Import):
                mods=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom):
                if node.level:
                    issue(name,"RELATIVE_IMPORT_NEEDS_EXPLICIT_BINDING",node.module or "");continue
                mods=[node.module] if node.module else []
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ("__import__","eval","exec"):
                issue(name,"DYNAMIC_IMPORT_OR_EXEC",node.func.id)
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=="import_module":
                issue(name,"DYNAMIC_IMPORT_MODULE",node.func.attr)
            for mod in mods:
                if mod.startswith(("tools.","tests.")):
                    path=mod.replace(".","/")+".py"
                    if (root/path).is_file(): deps.add(path)
                    elif (root/mod.replace(".","/")/"__init__.py").is_file():
                        deps.add(mod.replace(".","/")+"/__init__.py")
                    else: issue(name,"UNRESOLVED_LOCAL_IMPORT",mod)
                elif mod in ("tools","tests"):
                    continue
                elif mod.split(".")[0] not in sys.stdlib_module_names:
                    issue(name,"NON_STDLIB_IMPORT_REQUIRES_BINDING",mod)
        checked[name]=sorted(deps)
        active.remove(name)
        for dep in sorted(deps): visit(dep)
    for item in sorted(set(names)):
        if item.endswith(".py"):visit(item)
        else:
            rel=PurePosixPath(item)
            if rel.is_absolute() or ".." in rel.parts or rel.as_posix()!=item:
                issue(item,"UNSAFE_NON_PYTHON_SOURCE")
            elif (root/item).is_symlink() or not (root/item).is_file():
                issue(item,"NON_PYTHON_SOURCE_MISSING")
    return {"schema":"enguru.suzgec.v24.transitive-static-closure/v1",
            "scope":"LOCAL_PYTHON_TRANSITIVE_STATIC_IMPORTS_ONLY",
            "state":"PASS_BOUNDED_STATIC_CLOSURE_ONLY" if not findings else "HOLD_GUVENLI_DUR",
            "checked":checked,"blockers":findings,
            "runtimeDependencyClosure":"HOLD_NOT_PROVEN",
            "nativeAuthority":"HOLD","verifiedFinish":"HOLD"}

if __name__=="__main__":
    from tools.enguru_suzgec_v24_delivery_inventory import FILES
    print(json.dumps(assess(Path(__file__).resolve().parents[1],FILES),sort_keys=True))
