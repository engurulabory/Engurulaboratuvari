"""V5 Mac operator: migrate independently, one active launchd, V4 backup preserved.

Reuses V4 transport; stores V5 diagnostic learning in the existing SQLite file.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import plistlib
import sqlite3
import sys
from tools import enguru_mk_bridge_v1 as bridge
from tools import enguru_mk_autopilot_v4 as v4
from tools import enguru_mk_autopilot_v1 as v3
from tools import enguru_mk_intelligence_v5 as mind

LABEL='com.enguru.mk.bridge.pilot-v5'
RUNTIME='enguru-mk-bridge-pilot-v5.zip'

def cycle():
    # Transport first; stop on error, maintain the prior V4 HOLD behavior.
    old=v4.cycle()
    root,pilot,_=v4._paths()
    ledger=bridge.LocalLedger(root/'bridge.sqlite')
    try:
        token,_,_=v3.cached_credentials()
        api=bridge.GitHubAPI(token)
        h=api.branch_head();api.ensure_forward(ledger.last_remote(),h)
        received=0;states={}
        for name in api.listing(bridge.ROOT+'/diagnostics/github',h):
            raw=api.content(bridge.ROOT+'/diagnostics/github/'+name,h)
            source=api.content(bridge.ROOT+'/streams/github/'+name,h)
            if source is None or raw is None:raise mind.Hold('HOLD_DIAG_SOURCE_REQUIRED')
            ev=bridge.parse(source)
            report=mind.parse(raw)
            state=mind.accept_report(ledger.db,report,ev)
            received+=1;states[state]=states.get(state,0)+1
        # Also create local diagnosis for each Mac-origin event, but this does not auto-publish
        # to a public GitHub branch until an owner-reviewed workflow does so.
        local=0
        for event_id,raw in ledger.db.execute('SELECT event_id,raw FROM outgoing ORDER BY seq'):
            ev=bridge.parse(raw)
            rep=mind.assess(ev)
            if rep['producer']!='MAC_OSI_MK':raise mind.Hold('HOLD_LOCAL_PRODUCER')
            local+=1
        ledger.set_remote(api.branch_head())
        return {'state':'PASS_V5_DIAGNOSTIC_SYNC_ONLY','v4Transport':old['state'],
                'incomingDiagnosis':received,'outcomeStates':states,'localDiagnosisReviewed':local,
                'learning':mind.scorecard(ledger.db),'officialAcceptance':'HOLD','productWrites':0}
    finally:ledger.close()

def status():
    root,pilot,_=v4._paths()
    p=root/'bridge.sqlite'
    if p.is_symlink() or not p.is_file():raise mind.Hold('HOLD_LEDGER_REQUIRED')
    import urllib.parse
    uri='file:'+urllib.parse.quote(str(p),safe='/')+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as db:
        tables={x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'mk_v5_assessments' in tables:
            x=db.execute('SELECT count(*) FROM mk_v5_assessments').fetchone()[0]
            s=[{'reportId':a,'nextStep':b,'state':c} for a,b,c in db.execute('SELECT report_id,next_step,state FROM mk_v5_assessments ORDER BY report_id LIMIT 40')]
        else:x,s=0,[]
        return {'state':'PASS_V5_LOCAL_READONLY_STATUS','diagnosticsReceived':x,'alignedNextSteps':s,
                'officialAcceptance':'HOLD','productWrites':0}

def activate(archive):
    if sys.platform!='darwin':raise mind.Hold('HOLD_MAC_ONLY')
    root,pilot,_=v4._paths()
    if root.is_symlink() or not (root/'bridge.sqlite').is_file():raise mind.Hold('HOLD_EXISTING_V4_LEDGER_REQUIRED')
    token,binary,mode=v3.cached_credentials()
    # Important: new V5 install is first staged and backup completed before changing launchd.
    if not binary or not Path(binary).is_absolute():raise mind.Hold('HOLD_SAVED_AUTH_REQUIRED')
    archive_dir=Path.home()/'Desktop/AudiV13'
    if archive_dir.is_symlink() or not archive_dir.is_dir():raise mind.Hold('HOLD_BACKUP_DIRECTORY')
    from datetime import datetime,timezone
    snap=archive_dir/('ENGURU_MK_V5_PRE_UPGRADE_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+str(os.getpid())+'.sqlite')
    ledger=bridge.LocalLedger(root/'bridge.sqlite')
    try:bk_sha=ledger.backup(snap)
    finally:ledger.close()
    v3.safe_dir(pilot);v3.safe_dir(pilot/'logs')
    archive=Path(archive)
    if archive.is_symlink() or not archive.is_file():raise mind.Hold('HOLD_ZIP_INPUT')
    raw=archive.read_bytes();sha=bridge.sha(raw)
    runtime=pilot/RUNTIME
    copied=v3.create_once(runtime,raw,0o500)
    v3.verify_installed(runtime,sha)
    plist=Path.home()/'Library/LaunchAgents'/f'{LABEL}.plist'
    if plist.parent.is_symlink() or not plist.parent.is_dir():raise mind.Hold('HOLD_PLIST_DIRECTORY')
    p=plistlib.loads(v3.launch_plist(runtime,Path(sys.executable),binary,mode,pilot/'logs',sha))
    p['Label']=LABEL
    p['EnvironmentVariables']['ENGURU_MK_INSTALLED_SHA256']=sha
    desc=plistlib.dumps(p,sort_keys=True)
    # Preserve old V4 plist and runtime; one active scheduled worker after switchover.
    uid=os.getuid();prior=f'gui/{uid}/{v4.LABEL}';new=f'gui/{uid}/{LABEL}'
    oldrunning=v4._out(['/bin/launchctl','print',prior],timeout=8).returncode==0
    if oldrunning:
        down=v4._out(['/bin/launchctl','bootout',prior],timeout=15)
        if down.returncode:raise mind.Hold('HOLD_PRIOR_AGENT_STOP')
    try:
        created=v3.create_once(plist,desc,0o600)
        result=v4._out(['/bin/launchctl','bootstrap',f'gui/{uid}',str(plist)],timeout=20)
        if result.returncode and v4._out(['/bin/launchctl','print',new],timeout=8).returncode:
            raise mind.Hold('HOLD_NEW_AGENT_START')
        initial='HOLD_NETWORK_RETRY'
        try:initial=cycle()['state']
        except (bridge.Hold,mind.Hold,OSError) as e:initial='HOLD_'+type(e).__name__
    except Exception:
        if oldrunning:
            v4_plist=Path.home()/'Library/LaunchAgents'/f'{v4.LABEL}.plist'
            if v4_plist.is_file():v4._out(['/bin/launchctl','bootstrap',f'gui/{uid}',str(v4_plist)],timeout=15)
        raise
    return {'state':'PASS_V5_LOCAL_ACTIVATION','zipSha256':sha,'backup':str(snap),
            'backupSha256':bk_sha,'runtime':str(runtime),'launchd':created,
            'firstCycle':initial,'previousV4Files':'PRESERVED','officialAcceptance':'HOLD','productWrites':0}

def main():
    try:
        if sys.argv[1:]==['--activate']:res=activate(Path(sys.argv[0]))
        elif sys.argv[1:]==['--cycle']:res=cycle()
        elif sys.argv[1:]==['--status']:res=status()
        else:raise mind.Hold('HOLD_V5_COMMAND')
        print(json.dumps(res,sort_keys=True,ensure_ascii=False))
    except (bridge.Hold,mind.Hold,sqlite3.Error,OSError,ValueError,TypeError) as e:
        print('STATE=HOLD_GUVENLI_DUR; REASON='+str(e));raise SystemExit(50)
if __name__=='__main__':main()
