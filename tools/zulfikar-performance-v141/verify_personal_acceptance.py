"""Reconcile preserved technical evidence for the owner's new scope; no issuer or task runner."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile

BASE = Path('tools/zulfikar-performance-v141')
CONTRACT = BASE / 'PERSONAL_USE_ACCEPTANCE_V1.json'
HEAD = '904ef5c6bf0b9247b25c774c9cca195262c16bc2'
REPO = 'engurulabory/Engurulaboratuvari'
ALLOWED = {str(CONTRACT), str(BASE / 'PERSONAL_USE_DONECHECK_V1.md'),
           str(BASE / 'verify_personal_acceptance.py'), '.github/workflows/enguru-zulfikar-performance.yml'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def reusable():
    if not CONTRACT.is_file():
        return False
    subprocess.run(['git', 'merge-base', '--is-ancestor', HEAD, 'HEAD'], check=True)
    changes = set(git('diff', '--name-only', HEAD, 'HEAD').splitlines())
    return bool(changes) and changes <= ALLOWED

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def api_bytes(suffix):
    request = urllib.request.Request('https://api.github.com/repos/' + REPO + suffix,
        headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                 'Accept': 'application/vnd.github+json'})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=45) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code not in (301, 302, 303, 307, 308):
            raise
        location = error.headers['Location']
        assert location.startswith('https://')
        # GitHub credentials never accompany the signed object-store URL.
        with urllib.request.urlopen(location, timeout=45) as response:
            return response.read()

def api(suffix):
    return json.loads(api_bytes(suffix))

def extract(data, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        assert len(entries) < 2000 and sum(x.file_size for x in entries) < 20_000_000
        assert len({x.filename for x in entries}) == len(entries)
        for entry in entries:
            name = Path(entry.filename)
            assert not name.is_absolute() and '..' not in name.parts and '\\' not in entry.filename
            assert (entry.external_attr >> 16) & 0o170000 != 0o120000
        archive.extractall(destination)

def verify():
    assert reusable(), 'HOLD_SOURCE_DRIFT: preserved campaign source must be identical'
    contract = read(CONTRACT)
    assert contract['version'] == '1.0.0' and contract['baselineHead'] == HEAD
    assert [x['id'] for x in contract['criteria']] == [
        'PERSONAL-REAL-WORK', 'PERSONAL-CORRECTNESS', 'PERSONAL-PROVEN-CLOSURE']
    assert set(contract['legacyExternalConditions'].values()) == {'HOLD'}
    assert sha(Path(contract['legacyContract']).read_bytes()) == contract['legacyContractSha256']
    assert contract['closure']['MAC_OSI_FIELD_ACCEPTANCE'] == 'NOT_TESTED'
    assert contract['closure']['LEGACY_VERIFIED_FINISH'] == 'HOLD'
    current = git('rev-parse', 'HEAD')
    assert current == os.environ['EXPECTED_ENGINE_HEAD']
    assert os.environ['GITHUB_REPOSITORY'] == REPO
    destination = Path('evidence/personal-use')
    destination.mkdir(parents=True, exist_ok=True)
    ci = []
    for run_id in contract['baselineCiRunIds']:
        run = api('/actions/runs/' + str(run_id))
        assert run['head_sha'] == HEAD and run['conclusion'] == 'success'
        ci.append({'id': run_id, 'head': run['head_sha'], 'conclusion': run['conclusion']})
    assert len(ci) == 6
    downloads = []
    for artifact in contract['artifacts']:
        endpoint = '/actions/artifacts/' + str(artifact['id'])
        metadata = api(endpoint)
        assert not metadata['expired'] and metadata['workflow_run']['head_sha'] == HEAD
        assert metadata['digest'] == 'sha256:' + artifact['sha256']
        data = api_bytes(endpoint + '/zip')
        assert sha(data) == artifact['sha256']
        (destination / (str(artifact['id']) + '.zip')).write_bytes(data)
        extract(data, destination / artifact['directory'])
        downloads.append({'id': artifact['id'], 'sha256': sha(data)})
    inner = (destination / 'second-outer/second-exam-evidence.zip').read_bytes()
    assert sha(inner) == contract['secondInnerSha256']
    second_root = destination / 'second'
    extract(inner, second_root)
    manifest = read(second_root / 'BYTE_MANIFEST.json')
    assert len(manifest) == 127
    for name, pin in manifest.items():
        assert sha((second_root / name).read_bytes()) == pin
    assert (second_root / 'source-commit.txt').read_text().strip() == HEAD
    report_bytes = (destination / 'engine/engine-donecheck.json').read_bytes()
    assert sha(report_bytes) == contract['donecheck']['reportSha256']
    report = json.loads(report_bytes)
    assert report['sourceHead'] == HEAD
    assert report['donecheckSource'] == contract['donecheck']['sourceHead']
    machine, full = report['machineVerification'], report['fullVerification']
    assert machine['id'] == contract['donecheck']['technicalResultId'] and machine['outcome'] == 'pass'
    assert full['id'] == contract['donecheck']['fullResultId'] and full['outcome'] == 'inconclusive'
    assert len(machine['criteria']) == 4 and len(full['criteria']) == 7
    assert sum(x['outcome'] == 'inconclusive' for x in full['criteria']) == 3
    assert report['officialVerifiedFinish'] == 'HOLD' and not report['recordVerifiedFinishInvoked']
    for name, pin in report['filePins'].items():
        mapped = name.replace('evidence/engine-final', str(destination / 'engine')).replace(
            'evidence/second-exam', str(second_root)).replace('evidence/performance', str(destination / 'performance'))
        assert sha(Path(mapped).read_bytes()) == pin
    for name, count in [('round-1-source.log', 34), ('round-2-resilience.log', 6), ('round-3-finish.log', 33)]:
        log = (destination / 'engine' / name).read_text()
        assert re.search(r'Ran ' + str(count) + r' tests?\b', log) and re.search(r'\nOK\s*$', log)
    job = api('/actions/jobs/' + str(contract['regressionJobId']))
    assert job['run_id'] == 40396686822 and job['conclusion'] == 'success'
    regression = api_bytes('/actions/jobs/' + str(contract['regressionJobId']) + '/logs')
    assert b'"tests": 378' in regression and b'DOM_EXACT_SOURCE_CI_TESTS_PASS' in regression
    (destination / 'preserved-378-regression.log').write_bytes(regression)
    for round_id in (1, 2, 3):
        subprocess.run([sys.executable, '-B', str(BASE / 'verify_campaign.py'),
                        str(destination / 'performance' / ('round-' + str(round_id)))], check=True)
    subprocess.run([sys.executable, '-B', str(BASE / 'second-exam/verify_package.py'), str(second_root)], check=True)
    passed = {x['criterionId'] for x in machine['criteria'] if x['outcome'] == 'pass'}
    assert all(set(x['legacyTechnicalCriteria']) <= passed for x in contract['criteria'])
    result = {'schema': 'enguru.zulfikar.personal-use-technical-receipt/v1', 'sourceHead': current,
        'baselineHead': HEAD, 'contractVersion': contract['version'], 'contractSha256': sha(CONTRACT.read_bytes()),
        'githubRunId': os.environ['GITHUB_RUN_ID'], 'criteria': {x['id']: 'PASS' for x in contract['criteria']},
        'preservedCi': ci, 'preservedArtifacts': downloads, 'innerManifest': '127/127',
        'technicalVerificationResultId': machine['id'], 'legacyFullVerificationResultId': full['id'],
        'newVerificationResultIssued': False, 'PERSONAL_USE_TECHNICAL_ACCEPTANCE': 'PASS',
        'GITHUB_ENGINEERING_ACCEPTANCE': 'PENDING_ALL_CURRENT_REPOSITORY_CI',
        'MAC_OSI_FIELD_ACCEPTANCE': 'NOT_TESTED', 'LEGACY_VERIFIED_FINISH': 'HOLD',
        'newTaskProcesses': 0, 'signatureOrLedgerWrite': False}
    (destination / 'personal-use-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    if sys.argv[1:] == ['--classify']:
        print('true' if reusable() else 'false')
    elif sys.argv[1:] == ['--verify']:
        verify()
    else:
        raise SystemExit('Use --classify or --verify')
