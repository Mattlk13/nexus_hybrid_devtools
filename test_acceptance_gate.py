import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from ci import run_sentry_acceptance as gate

class HostedAcceptanceGateTests(unittest.TestCase):
    def run_gate(self, env, suite=None):
        with tempfile.TemporaryDirectory() as root, contextlib.chdir(root), patch.dict(os.environ,env,clear=True):
            output=io.StringIO()
            with patch.object(gate.unittest.defaultTestLoader,'loadTestsFromName',return_value=suite) as loader, contextlib.redirect_stdout(output):
                code=gate.main()
            return code,json.loads(Path('evidence/sentry-acceptance.json').read_text()),output.getvalue(),loader.called
    def test_missing_configuration_blocks_without_running_provider(self):
        code,report,output,called=self.run_gate({})
        self.assertEqual(code,2);self.assertEqual(report['status'],'BLOCKED')
        self.assertEqual(set(report['missing_configuration']),set(gate.REQUIRED))
        self.assertFalse(called)
    def test_wrong_organization_blocks_without_running_provider(self):
        env={name:'SECRET_fixture' for name in gate.REQUIRED}
        env['NEXUS_SENTRY_CERTIFICATION_ORG']='different'
        code,report,output,called=self.run_gate(env)
        self.assertEqual(code,2);self.assertFalse(called);self.assertNotIn('SECRET_fixture',output)
    def test_skipped_acceptance_never_passes(self):
        class Skipped(unittest.TestCase):
            @unittest.skip('fixture')
            def runTest(self): pass
        code,report,_,_=self.run_gate({n:'fixture' for n in gate.REQUIRED},unittest.TestSuite([Skipped()]))
        self.assertEqual(code,1);self.assertEqual(report['status'],'FAIL')
        self.assertEqual(report['skips'],1)
    def test_exception_details_never_leak_into_evidence(self):
        class Failing(unittest.TestCase):
            def runTest(self): raise RuntimeError('SECRET_fixture')
        code,report,output,_=self.run_gate({n:'SECRET_fixture' for n in gate.REQUIRED},unittest.TestSuite([Failing()]))
        self.assertEqual(code,1);self.assertNotIn('SECRET_fixture',output)
        self.assertNotIn('SECRET_fixture',json.dumps(report))
