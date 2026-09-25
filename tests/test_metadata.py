import importlib.util
from pathlib import Path
import unittest
from sf_agent import engine
from sf_agent.validation import load_json

class Metadata(unittest.TestCase):
    def test_source_anchors_have_dates_and_status(self):
        sources=load_json(engine.ROOT/'references/standards.json')['standards']
        for source in sources:
            self.assertTrue(source['url'].startswith('https://'));self.assertIn('checked_on',source);self.assertIn('status',source)
    def test_capability_boundaries(self):
        capabilities=engine.config()['capabilities']
        for name in ('embedded_llm','live_data','trade_execution','scheduler'): self.assertIs(capabilities[name],False)
    def test_shared_module_count(self):
        manifest=load_json(engine.ROOT/'COMMON_CORE_MANIFEST.json');self.assertNotIn('analytics.py',manifest['files']);self.assertIn('engine.py',manifest['files'])
    def test_repository_owner(self): self.assertEqual(load_json(engine.ROOT/'repository-metadata.json')['owner'],'HHFinAi')
    def test_source_study_is_not_research_mode(self): self.assertEqual(load_json(engine.ROOT/'examples/source-study-request.json')['mode'],'source-study')
if __name__=='__main__': unittest.main()
