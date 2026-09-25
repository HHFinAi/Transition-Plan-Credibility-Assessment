from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from sf_agent.__main__ import main
from sf_agent import engine

class CLI(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def call(self,args):
        out=io.StringIO();err=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err): code=main(args)
        return code,out.getvalue(),err.getvalue()
    def test_routes(self):
        code,out,_=self.call(['routes']);self.assertEqual(code,0);self.assertEqual(len(json.loads(out)),3)
    def test_demo_status_report_export(self):
        run=str(self.base/'run');export=str(self.base/'export')
        self.assertEqual(self.call(['demo','--out',run])[0],0)
        self.assertEqual(json.loads(self.call(['status','--run',run])[1])['status'],'SYNTHETIC_COMPLETE_NOT_APPROVED')
        self.assertIn('NOT INVESTMENT RESEARCH APPROVED',self.call(['report','--run',run])[1])
        self.assertEqual(self.call(['export','--run',run,'--out',export])[0],0)
        self.assertEqual(len(list(Path(export).iterdir())),4)
    def test_source_study(self):
        code,out,_=self.call(['source-study','--out',str(self.base/'study')]);self.assertEqual(code,0);self.assertEqual(json.loads(out)['status'],'NEEDS_DATA')
    def test_calc(self):
        code,out,_=self.call(['calc','--operation',engine.config()['demo_operation'],'--arguments',str(engine.ROOT/'examples/calculation-arguments.json')]);self.assertEqual(code,0);self.assertIn('input_provenance',json.loads(out))
    def test_invalid_file(self):
        code,_,err=self.call(['init','--request',str(self.base/'absent.json'),'--out',str(self.base/'run')]);self.assertEqual(code,2);self.assertIn('ERROR',err)
    def test_unknown_demo_route(self):
        self.assertEqual(self.call(['demo','--out',str(self.base/'run'),'--route','invalid'])[0],2)
    def test_review_cli_flag_does_not_approve_demo(self):
        run=str(self.base/'run');_,out,_=self.call(['demo','--out',run]);revision=json.loads(out)['revision']
        code,_,err=self.call(['review','--run',run,'--reviewer','TEST reviewer','--decision','APPROVE_RESEARCH','--rationale','test only','--revision',str(revision),'--attest-human'])
        self.assertEqual(code,2);self.assertIn('cannot receive research approval',err)

if __name__=='__main__': unittest.main()
