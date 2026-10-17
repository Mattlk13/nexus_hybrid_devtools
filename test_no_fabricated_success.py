import asyncio
import unittest
from nexus_hybrid_devtools import DevToolsEngine

class TestDevtools(unittest.TestCase):
    def test_setup_never_claims_success(self):
        engine = DevToolsEngine()
        result = asyncio.run(engine.setup_error_tracking("example"))
        self.assertFalse(result["success"])
        self.assertFalse(result["sentry_enabled"])
        self.assertNotIn("dsn", result)

    def test_pipeline_never_claims_success(self):
        result = asyncio.run(DevToolsEngine().create_ci_pipeline({"stages": ["build"]}))
        self.assertFalse(result["success"])
        self.assertNotIn("pipeline", result)

if __name__ == "__main__":
    unittest.main()
