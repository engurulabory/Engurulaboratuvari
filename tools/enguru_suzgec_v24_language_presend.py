#!/usr/bin/env python3
"""ENGURU Suzgec v2.4 candidate: a fail-closed pre-send adapter, reusing L01–L18 governance.

This adapter evaluates explicit drafts only. Live ChatGPT/Work surface hooks and
human semantic acceptance retain independent authority.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, sys
from pathlib import Path

CONTRACT = 'governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json'
SCHEMA = 'enguru.suzgec.v24.scoped-language-presend/v1'
RISK = (
  ('POSITIVE_PRESERVE', re.compile(r'(?iu)\bdeğiştirmez\b'), 'Kaynak bütünlüğünü korur.'),
  ('POSITIVE_PRESERVE', re.compile(r'(?iu)\bdokunmaz\b'), 'Mevcut kaynakları korur.'),
  ('CANONICAL_HOLD', re.compile(r'(?iu)\bPASS\s+değil\b'), 'STATE=HOLD; açılma koşulunu ve sonraki eylemi belirt.'),
)
class LanguageHold(Exception):
    pass

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_contract(root: Path) -> dict:
    path=root/CONTRACT
    if path.is_symlink() or not path.is_file(): raise LanguageHold('CONTRACT_SOURCE_REQUIRED')
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('schema')!='enguru.suzgec.v24.language-alignment-contract/v1':raise LanguageHold('CONTRACT_SCHEMA')
    if data.get('candidateVersion')!='2.4' or data.get('canonicalInstalledVersion')!='2.3':raise LanguageHold('VERSION_SCOPE')
    if [x.get('id') for x in data.get('engineeringWorklist',[])] != ['D01_CANONICAL_UNIVERSE','D02_POSITIVE_STATE_LANGUAGE','D03_PRESEND_GATE','D04_ADVERSARIAL_REGRESSION','D05_CROSS_SURFACE_ACCEPTANCE']:raise LanguageHold('WORKLIST_DRIFT')
    if data.get('existingFinishGates')!=['T01','T02','T03','T04'] or len(data.get('eightStages',[]))!=8:raise LanguageHold('CANONICAL_STAGE_DRIFT')
    if data.get('p01')!='SUSPENDED' or data.get('verifiedFinish')!='HOLD':raise LanguageHold('AUTHORITY_DRIFT')
    rules=data['languageRules']
    if rules.get('canonicalIds') != [f'L{i:02d}' for i in range(1,19)]:raise LanguageHold('LANGUAGE_RULE_DRIFT')
    return data

def _visible_lines(text: str):
    fenced=False
    for index,line in enumerate(text.splitlines(),1):
        if line.lstrip().startswith(('```','~~~')):
            fenced=not fenced
            continue
        # Quotations and code examples are evidence of the source wording.
        if fenced or line.lstrip().startswith(('>','    ','|')):
            continue
        yield index,line

def inspect(text: str, root: Path, surface: str='OSi') -> dict:
    output={'schema':SCHEMA,'surface':surface,'state':'HOLD','p01':'SUSPENDED','technicalFinish':'HOLD','verifiedFinish':'HOLD','crossSurfaceAcceptance':'HOLD','fullL01L18Acceptance':'HOLD_SEMANTIC_AND_FIELD_REVIEW'}
    if surface not in ('OSi','ChatGPT','Work'):
        output['reason']='UNSUPPORTED_SURFACE';return output
    if not text or not text.strip():output['reason']='EMPTY_DRAFT';return output
    try:
        c=load_contract(root)
        src=root/c['languageRules']['automatedLinterPath']
        if src.is_symlink() or not src.is_file():raise LanguageHold('CANONICAL_LINTER_MISSING')
        if sha(src.read_bytes())!=c['languageRules']['automatedLinterSha256']:raise LanguageHold('CANONICAL_LINTER_SOURCE_DRIFT')
        spec=importlib.util.spec_from_file_location('enguru_v24_pinned_linter',src)
        if spec is None or spec.loader is None:raise LanguageHold('CANONICAL_LINTER_IMPORT')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        if not callable(getattr(mod,'lint',None)):raise LanguageHold('CANONICAL_LINTER_INTERFACE')
        checked=mod.lint(text,strict=True)
        if not isinstance(checked,dict):raise LanguageHold('CANONICAL_LINTER_RESULT')
        output['canonicalLinterSha256']=sha(src.read_bytes())
        output['contractSha256']=sha((root/CONTRACT).read_bytes())
        output['draftSha256']=sha(text.encode('utf-8'))
        output['checkedRuleIds']=checked.get('checked_rules',[])
        output['canonicalLinterState']=checked.get('state')
        findings=list(checked.get('findings') or [])
        for ln,line in _visible_lines(text):
            for rule,pattern,recommendation in RISK:
                if pattern.search(line):
                    findings.append({'rule':rule,'severity':'MATERIAL','line':ln,'recommendedValidState':recommendation})
        output['findings']=findings
        output['findingCount']=len(findings)
        if checked.get('state')!='PASS' or findings:
            output['reason']='DRAFT_LANGUAGE_GATE_HOLD';return output
        output['state']='PASS_SCOPED_DRAFT_LANGUAGE_GATE'
        output['reason']='SEMANTIC_REVIEW_AND_REAL_SURFACE_OBSERVATION_PENDING'
        return output
    except (LanguageHold,ValueError,KeyError,TypeError) as exc:
        output['reason']=str(exc) or type(exc).__name__
        return output

def main() -> int:
    ap=argparse.ArgumentParser(description='ENGURU v2.4 language presend adapter (scoped draft check)')
    ap.add_argument('draft_file',help='Local UTF-8 draft text file')
    ap.add_argument('--surface',choices=['OSi','ChatGPT','Work'],default='OSi')
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    a=ap.parse_args()
    try: text=Path(a.draft_file).read_text(encoding='utf-8')
    except Exception: text=''
    result=inspect(text,a.root,a.surface)
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if result['state']=='PASS_SCOPED_DRAFT_LANGUAGE_GATE' else 20

if __name__=='__main__':raise SystemExit(main())
