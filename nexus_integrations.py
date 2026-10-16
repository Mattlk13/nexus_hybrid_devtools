"""Authenticated Sentry and Jenkins provisioning adapters.

Operations are opt-in via environment configuration and verify remote state before
reporting success. No credentials are returned in tool results.
"""
import base64
import json
import os
from urllib import error, parse, request


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise IntegrationError("redirect_rejected")


def _open(req, timeout=15):
    return request.build_opener(_NoRedirect()).open(req, timeout=timeout)


class IntegrationError(RuntimeError):
    pass


def _json_request(url, *, method="GET", headers=None, payload=None, timeout=15):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with _open(req, timeout=timeout) as response:
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise IntegrationError("response_too_large")
            value = json.loads(raw) if raw else {}
            if not isinstance(value, dict):
                raise IntegrationError("invalid_response_schema")
            return response.status, value
    except error.HTTPError as exc:
        code = {401: "authentication_failed", 403: "permission_denied", 409: "duplicate_conflict"}.get(exc.code, "remote_http_error")
        raise IntegrationError(code) from exc
    except (error.URLError, ValueError, TimeoutError) as exc:
        raise IntegrationError("remote_request_failed") from exc


def provision_sentry(project):
    token = os.getenv("NEXUS_SENTRY_TOKEN")
    org = os.getenv("NEXUS_SENTRY_ORG")
    if not token or not org:
        raise IntegrationError("sentry_credentials_not_configured")
    if not project or not isinstance(project, str):
        raise IntegrationError("project_required")
    base = "https://sentry.io/api/0"
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    orgpath = parse.quote(org, safe="")
    status, result = _json_request(
        base + "/teams/" + orgpath + "/" + parse.quote(os.environ.get("NEXUS_SENTRY_TEAM", "default"), safe="") + "/projects/",
        method="POST", headers=headers,
        payload={"name": project, "slug": project.lower().replace(" ", "-")})
    if status not in (200, 201) or not result.get("slug"):
        raise IntegrationError("sentry_creation_unconfirmed")
    slug = result["slug"]
    check, verified = _json_request(
        base + "/projects/" + orgpath + "/" + parse.quote(slug, safe="") + "/",
        headers=headers)
    if check != 200 or verified.get("slug") != slug:
        raise IntegrationError("sentry_verification_failed")
    return {"success": True, "project": project, "slug": slug, "sentry_enabled": True}


def provision_jenkins(config):
    base = os.getenv("NEXUS_JENKINS_URL", "").rstrip("/")
    user = os.getenv("NEXUS_JENKINS_USER")
    token = os.getenv("NEXUS_JENKINS_TOKEN")
    parsed = parse.urlsplit(base)
    if not (base and user and token) or parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise IntegrationError("jenkins_credentials_or_https_not_configured")
    name = config.get("name") if isinstance(config, dict) else None
    xml = config.get("config_xml") if isinstance(config, dict) else None
    if not isinstance(name, str) or not name.strip() or not isinstance(xml, str) or not xml.strip():
        raise IntegrationError("jenkins_name_and_config_xml_required")
    auth = base64.b64encode((user + ":" + token).encode()).decode()
    headers = {"Authorization": "Basic " + auth}
    # Jenkins API-token authentication is exempt from CSRF crumbs.
    target = base + "/createItem?name=" + parse.quote(name, safe="")
    req = request.Request(target, data=xml.encode(), method="POST",
                          headers={**headers, "Content-Type": "application/xml"})
    try:
        with _open(req, timeout=15) as response:
            if response.status not in (200, 201, 302):
                raise IntegrationError("jenkins_creation_unconfirmed")
    except error.URLError as exc:
        raise IntegrationError("jenkins_creation_failed") from exc
    status, payload = _json_request(
        base + "/job/" + parse.quote(name, safe="") + "/api/json",
        headers=headers)
    if status != 200 or payload.get("name") != name:
        raise IntegrationError("jenkins_verification_failed")
    return {"success": True, "pipeline": "jenkins", "name": name, "verified": True}
