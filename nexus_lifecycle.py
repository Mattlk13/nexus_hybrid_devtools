"""Idempotent certification-resource lifecycle with external readback.

Deletion is restricted to explicitly enabled nexus-cert-* fixtures. Receipts
must match the current remote resource ID; existing duplicates are never owned.
"""
import base64
import hashlib
import os
import re
from urllib import error, parse, request
from nexus_integrations import IntegrationError, _json_request, _open


def _read(url, headers):
    try:
        return _json_request(url, headers=headers)[1]
    except IntegrationError as exc:
        if str(exc) == 'not_found': return None
        raise


def _sentry():
    org=os.getenv('NEXUS_SENTRY_ORG');token=os.getenv('NEXUS_SENTRY_TOKEN')
    if not org or not token: raise IntegrationError('sentry_credentials_not_configured')
    return org, {'Authorization':'Bearer '+token,'Content-Type':'application/json'}


def sentry_create(project):
    org,headers=_sentry()
    if not isinstance(project,str) or not re.fullmatch(r'nexus-cert-[a-z0-9-]{1,40}',project):
        raise IntegrationError('certification_project_required')
    base='https://sentry.io/api/0';url=base+'/projects/'+parse.quote(org,safe='')+'/'+project+'/'
    existing=_read(url,headers)
    if existing:
        if existing.get('slug')!=project or not existing.get('id'): raise IntegrationError('sentry_identity_conflict')
        return {'success':True,'duplicate':True,'created':False,'verified':True,'id':str(existing['id']),'slug':project,'org':org}
    try:
        _json_request(base+'/teams/'+parse.quote(org,safe='')+'/'+parse.quote(os.getenv('NEXUS_SENTRY_TEAM','default'),safe='')+'/projects/',
                      method='POST',headers=headers,payload={'name':project,'slug':project})
    except IntegrationError as exc:
        # Reconcile ambiguous network outcomes, but do not claim ownership.
        if str(exc) not in ('duplicate_conflict','remote_request_failed'): raise
        verified=_read(url,headers)
        if verified and verified.get('slug')==project and verified.get('id'):
            return {'success':True,'duplicate':True,'created':False,'verified':True,'id':str(verified['id']),'slug':project,'org':org}
        raise IntegrationError('sentry_outcome_unconfirmed') from exc
    verified=_read(url,headers)
    if not verified or verified.get('slug')!=project or not verified.get('id'):
        raise IntegrationError('sentry_verification_failed')
    return {'success':True,'duplicate':False,'created':True,'verified':True,'id':str(verified['id']),'slug':project,'org':org}


def sentry_rollback(receipt):
    org,headers=_sentry()
    if os.getenv('NEXUS_ALLOW_CERTIFICATION_DELETE')!='1' or not isinstance(receipt,dict) or receipt.get('created') is not True or receipt.get('org')!=org:
        raise IntegrationError('rollback_not_authorized')
    slug=receipt.get('slug','')
    if not re.fullmatch(r'nexus-cert-[a-z0-9-]{1,40}',slug): raise IntegrationError('rollback_scope_rejected')
    url='https://sentry.io/api/0/projects/'+parse.quote(org,safe='')+'/'+slug+'/'
    current=_read(url,headers)
    if current is None: return {'success':True,'deleted':True,'verified':True,'duplicate':True}
    if str(current.get('id'))!=receipt.get('id'): raise IntegrationError('rollback_identity_conflict')
    _json_request(url,method='DELETE',headers=headers)
    if _read(url,headers) is not None: raise IntegrationError('rollback_pending')
    return {'success':True,'deleted':True,'verified':True}


def _jenkins():
    base=os.getenv('NEXUS_JENKINS_URL','').rstrip('/');user=os.getenv('NEXUS_JENKINS_USER');token=os.getenv('NEXUS_JENKINS_TOKEN')
    parsed=parse.urlsplit(base)
    loopback=(os.getenv('NEXUS_JENKINS_LOOPBACK_FIXTURE')=='1' and parsed.scheme=='http' and parsed.hostname=='127.0.0.1')
    if not user or not token or not parsed.hostname or (parsed.scheme!='https' and not loopback) or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise IntegrationError('jenkins_credentials_or_https_not_configured')
    return base,{'Authorization':'Basic '+base64.b64encode((user+':'+token).encode()).decode()}


def _jenkins_call(url,headers,method='GET',body=None):
    try:
        with _open(request.Request(url,headers=headers,method=method,data=body),timeout=15) as response:
            data=response.read(1048577)
            if len(data)>1048576: raise IntegrationError('response_too_large')
            return data
    except error.HTTPError as exc:
        raise IntegrationError({400:'duplicate_conflict',401:'authentication_failed',403:'permission_denied',404:'not_found'}.get(exc.code,'remote_http_error')) from exc
    except (error.URLError,TimeoutError) as exc:
        raise IntegrationError('remote_request_failed') from exc


def _config(url,headers):
    try: return _jenkins_call(url+'/config.xml',headers)
    except IntegrationError as exc:
        if str(exc)=='not_found': return None
        raise


def jenkins_create(config):
    base,headers=_jenkins()
    name=config.get('name') if isinstance(config,dict) else None
    xml=config.get('config_xml') if isinstance(config,dict) else None
    if not isinstance(name,str) or not re.fullmatch(r'nexus-cert-[a-z0-9-]{1,40}',name) or not isinstance(xml,str):
        raise IntegrationError('certification_job_required')
    # Jenkins normalizes XML. Compare a caller-independent marker embedded in
    # the disabled job's description rather than unstable serialized bytes.
    if '<disabled>true</disabled>' not in xml or '<builders/>' not in xml:
        raise IntegrationError('disabled_fixture_required')
    import xml.etree.ElementTree as ET
    try:
        root=ET.fromstring(xml)
    except ET.ParseError as exc: raise IntegrationError('invalid_job_xml') from exc
    if root.tag!='project' or any(child.tag not in ('description','disabled','builders') for child in root):
        raise IntegrationError('unsupported_fixture_xml')
    builders=root.find('builders')
    if builders is None or len(builders) or root.findtext('disabled')!='true': raise IntegrationError('disabled_fixture_required')
    fingerprint=hashlib.sha256(xml.encode()).hexdigest()
    marker='nexus-cert:'+fingerprint
    description=root.find('description')
    if description is None: description=ET.SubElement(root,'description')
    description.text=marker
    payload=ET.tostring(root,encoding='utf-8')
    url=base+'/job/'+name
    def matches(data):
        try:
            tree=ET.fromstring(data)
            return tree.findtext('description')==marker and tree.findtext('disabled')=='true' and len(tree.find('builders'))==0
        except (ET.ParseError,TypeError): return False
    existing=_config(url,headers)
    if existing is not None:
        if not matches(existing): raise IntegrationError('duplicate_request_conflict')
        return {'success':True,'created':False,'duplicate':True,'verified':True,'name':name,'marker':marker,'base':base}
    try: _jenkins_call(base+'/createItem?name='+name,{**headers,'Content-Type':'application/xml'},'POST',payload)
    except IntegrationError as exc:
        if str(exc) not in ('duplicate_conflict','remote_request_failed'): raise
        data=_config(url,headers)
        if data is not None and matches(data):
            return {'success':True,'created':False,'duplicate':True,'verified':True,'name':name,'marker':marker,'base':base}
        raise IntegrationError('jenkins_outcome_unconfirmed') from exc
    if not matches(_config(url,headers)): raise IntegrationError('jenkins_verification_failed')
    return {'success':True,'created':True,'duplicate':False,'verified':True,'name':name,'marker':marker,'base':base}


def jenkins_rollback(receipt):
    base,headers=_jenkins()
    if os.getenv('NEXUS_ALLOW_CERTIFICATION_DELETE')!='1' or not isinstance(receipt,dict) or receipt.get('created') is not True or receipt.get('base')!=base:
        raise IntegrationError('rollback_not_authorized')
    name=receipt.get('name','')
    if not re.fullmatch(r'nexus-cert-[a-z0-9-]{1,40}',name): raise IntegrationError('rollback_scope_rejected')
    url=base+'/job/'+name
    data=_config(url,headers)
    if data is None: return {'success':True,'deleted':True,'verified':True,'duplicate':True}
    import xml.etree.ElementTree as ET
    if ET.fromstring(data).findtext('description')!=receipt.get('marker'): raise IntegrationError('rollback_identity_conflict')
    try: _jenkins_call(url+'/doDelete',headers,'POST',b'')
    except IntegrationError as exc:
        if str(exc)!='redirect_rejected': raise
    if _config(url,headers) is not None: raise IntegrationError('rollback_pending')
    return {'success':True,'deleted':True,'verified':True}
