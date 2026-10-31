"""Trusted local invocation authority, separate from model data; no global grants."""
import hashlib
import hmac
import json
import secrets
import time
from .contracts import Rejected, encoded
from .storage import read_private, write_new


class Authority:
    def __init__(self,root):
        path=root/'authority.key'
        try:self.key=read_private(path)
        except FileNotFoundError:
            try:write_new(path,secrets.token_bytes(32))
            except FileExistsError:pass
            self.key=read_private(path)
        if len(self.key)!=32:raise Rejected('KEY_FORMAT')

    def sign(self,data):return hmac.new(self.key,encoded(data),hashlib.sha256).hexdigest()

    def issue_local_pilot(self,plan,resource,now=None):
        # Invoked only by local owner UI/CLI bridge, never from role model JSON.
        g=dict(task=plan.task,plan=plan.sha,source=plan.source,scope=plan.scope,
               action='pilot.unique_jobs',resource=str(resource),
               expires=(int(time.time()) if now is None else now)+600,nonce=secrets.token_hex(24))
        return {'grant':g,'signature':self.sign(g)}

    def validate(self,envelope,plan,resource,now=None):
        if not isinstance(envelope,dict) or set(envelope)!={'grant','signature'}:raise Rejected('GRANT_FORMAT')
        g=envelope['grant']
        if not isinstance(g,dict) or not isinstance(envelope['signature'],str):raise Rejected('GRANT_FORMAT')
        if not hmac.compare_digest(self.sign(g),envelope['signature']):raise Rejected('GRANT_SIGNATURE')
        expected=dict(task=plan.task,plan=plan.sha,source=plan.source,scope=plan.scope,
                      action='pilot.unique_jobs',resource=str(resource))
        if set(g)!=set(expected)|{'expires','nonce'} or any(g[k]!=v for k,v in expected.items()):
            raise Rejected('GRANT_BINDING')
        if type(g['expires']) is not int or g['expires']<=(int(time.time()) if now is None else now):
            raise Rejected('GRANT_EXPIRED')
        if not isinstance(g['nonce'],str) or len(g['nonce'])!=48:raise Rejected('GRANT_NONCE')
        return g['nonce']


def tool_proposal(data,plan):
    if (not isinstance(data,dict) or set(data)!={'operation','plan_sha256'}
        or data['operation']!='apply_reviewed_unique_jobs_patch' or data['plan_sha256']!=plan.sha):
        raise Rejected('MODEL_PROPOSAL_IS_NOT_AUTHORITY')
    return 'apply_reviewed_unique_jobs_patch'
