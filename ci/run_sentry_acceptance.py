"""Hosted acceptance gate: missing configuration and skips cannot pass."""
import io
import json
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
REQUIRED = ("NEXUS_SENTRY_TOKEN", "NEXUS_SENTRY_ORG", "NEXUS_SENTRY_TEAM",
            "NEXUS_SENTRY_READONLY_TOKEN", "NEXUS_SENTRY_CERTIFICATION_ORG")
def main():
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    report = {"service": "hosted_sentry", "production": "HOLD", "status": "BLOCKED",
              "missing_configuration": missing, "tests_run": 0}
    if not missing and os.environ["NEXUS_SENTRY_ORG"] != os.environ["NEXUS_SENTRY_CERTIFICATION_ORG"]:
        report["reason"] = "isolated_organization_confirmation_mismatch"
    elif not missing:
        os.environ["NEXUS_SENTRY_LIVE_TESTS"] = "1"
        # Existing suite scopes resources to random nexus-cert-* projects and
        # verifies identity before cleanup. Never print provider exception data.
        suite = unittest.defaultTestLoader.loadTestsFromName("test_sentry_live")
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        report.update(tests_run=result.testsRun,
                      failures=len(result.failures), errors=len(result.errors),
                      skips=len(result.skipped),
                      failed_tests=[t.id() for t,_ in result.failures+result.errors])
        report["status"] = "PASS" if result.wasSuccessful() and result.testsRun and not result.skipped else "FAIL"
    output=Path("evidence")
    output.mkdir(exist_ok=True)
    (output/"sentry-acceptance.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))
    return 0 if report["status"]=="PASS" else 2 if report["status"]=="BLOCKED" else 1
if __name__=="__main__":
    raise SystemExit(main())
