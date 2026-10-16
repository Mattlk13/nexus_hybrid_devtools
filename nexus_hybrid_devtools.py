"""NEXUS development tools. Never report an external setup unless verified."""
import logging
import asyncio
from nexus_integrations import IntegrationError, provision_sentry, provision_jenkins
from typing import Dict

logger = logging.getLogger(__name__)


class DevToolsEngine:
    def __init__(self, db=None):
        self.db = db

    async def setup_error_tracking(self, project: str) -> Dict:
        """Sentry provisioning requires an authenticated provisioning adapter."""
        if not isinstance(project, str) or not project.strip():
            return {"success": False, "error": "project_required", "sentry_enabled": False}
        try:
            return await asyncio.to_thread(provision_sentry, project)
        except IntegrationError as exc:
            return {"success": False, "error": str(exc), "project": project,
                    "sentry_enabled": False}

    async def create_ci_pipeline(self, config: Dict) -> Dict:
        """No Jenkins job is created without a configured authenticated adapter."""
        if not isinstance(config, dict) or not config:
            return {"success": False, "error": "pipeline_configuration_required"}
        try:
            return await asyncio.to_thread(provision_jenkins, config)
        except IntegrationError as exc:
            return {"success": False, "error": str(exc)}

    def get_capabilities(self) -> Dict:
        return {"name": "Dev Tools Hybrid", "version": "1.0.1",
                "integrations": {"Sentry": "not_configured", "Jenkins": "not_configured",
                                 "Gitpod": "not_implemented", "ShellCheck": "not_implemented"}}


hybrid_devtools = DevToolsEngine(db=None)


def create_devtools_engine(db):
    global hybrid_devtools
    hybrid_devtools = DevToolsEngine(db)
    return hybrid_devtools
