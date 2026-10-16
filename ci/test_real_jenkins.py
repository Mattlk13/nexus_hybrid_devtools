"""Real ephemeral Jenkins; no production credentials or application jobs."""
import os
from pathlib import Path
import subprocess
import time
import unittest
from unittest.mock import patch
from nexus_lifecycle import jenkins_create,jenkins_rollback,IntegrationError

RUNTIME=os.getenv('NEXUS_TEST_RUNTIME','docker')

class RealJenkinsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.container='nexus-cert-jenkins-'+str(os.getpid())
        cls.receipt=None
        cls.image='nexus-cert-jenkins:2.580.1-matrix3.3'
        subprocess.run([RUNTIME,'build','-t',cls.image,'-f',str(Path(__file__).parent/'Jenkins.Dockerfile'),str(Path(__file__).parent)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=240)
        subprocess.run([RUNTIME,'run','-d','--name',cls.container,'--label','nexus.scope=certification',
                        '-p','127.0.0.1:18080:8080','--memory','1536m','--cpus','2','-e','JAVA_OPTS=-Djenkins.install.runSetupWizard=false',
                        '-v',str((Path(__file__).parent/'jenkins.groovy').resolve())+':/usr/share/jenkins/ref/init.groovy.d/certification.groovy:ro',
                        cls.image],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=240)
        cls.addClassCleanup(lambda:subprocess.run([RUNTIME,'rm','--force','--volumes',cls.container],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30))
        cls.tokens={}
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            for user in ('cert-admin','cert-reader'):
                r=subprocess.run([RUNTIME,'exec',cls.container,'cat','/var/jenkins_home/'+user+'.token'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=10)
                if r.returncode==0: cls.tokens[user]=r.stdout.decode().strip()
            if len(cls.tokens)==2:
                import urllib.request
                try:
                    # Ensure startup, not merely token-file creation, completed.
                    urllib.request.urlopen('http://127.0.0.1:18080/login',timeout=2).close()
                    break
                except Exception: pass
            time.sleep(2)
        else: raise RuntimeError('isolated_jenkins_startup_timeout')
        cls.env={'NEXUS_JENKINS_URL':'http://127.0.0.1:18080','NEXUS_JENKINS_LOOPBACK_FIXTURE':'1',
                 'NEXUS_JENKINS_USER':'cert-admin','NEXUS_JENKINS_TOKEN':cls.tokens['cert-admin'],
                 'NEXUS_ALLOW_CERTIFICATION_DELETE':'1'}
    def test_real_auth_duplicate_permission_and_rollback(self):
        config={'name':'nexus-cert-lifecycle','config_xml':'<project><description>fixture</description><disabled>true</disabled><builders/></project>'}
        with patch.dict(os.environ,self.env):
            receipt=jenkins_create(config)
            self.assertTrue(receipt['created'])
            try:
                duplicate=jenkins_create(config)
                self.assertTrue(duplicate['duplicate']);self.assertFalse(duplicate['created'])
                with patch.dict(os.environ,{'NEXUS_JENKINS_TOKEN':'invalid-fixture-token'}):
                    with self.assertRaisesRegex(IntegrationError,'authentication_failed|permission_denied'): jenkins_create(config)
                with patch.dict(os.environ,{'NEXUS_JENKINS_USER':'cert-reader','NEXUS_JENKINS_TOKEN':self.tokens['cert-reader']}):
                    with self.assertRaisesRegex(IntegrationError,'permission_denied'):
                        jenkins_create({**config,'name':'nexus-cert-forbidden'})
            finally:
                self.assertTrue(jenkins_rollback(receipt)['verified'])
            self.assertTrue(jenkins_rollback(receipt)['duplicate'])

if __name__=='__main__': unittest.main(verbosity=2)
