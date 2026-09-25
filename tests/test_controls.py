"""Workflow/data-control regression tests. All research-mode inputs here are TEST FIXTURES."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from sf_agent import engine
from sf_agent.analytics import OPERATIONS
from sf_agent.demo import calculation_record, fixture_artifact, run_demo, run_source_study, synthetic_request
from sf_agent.validation import DataError, load_json, validate_artifact, validate_dag, validate_expression, validate_request

class Controls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.request = synthetic_request()
        self.cfg = engine.config()
        self.standards = load_json(engine.ROOT/'references/standards.json')['standards']
    def tearDown(self):
        self.temp.cleanup()
    def start(self, request=None):
        return engine.start(request or self.request, self.base/'run')
    def art(self, state, sid='mandate'):
        return fixture_artifact(state, sid)
    def validate(self, art, state, sid='mandate'):
        validate_artifact(art,state['frozen']['stages'][sid],state['frozen']['request'],self.standards,OPERATIONS)
    def research_request(self):
        # Tests simulate reviewed records to exercise gates; not evidence of real research.
        req=copy.deepcopy(self.request);req['mode']='research';req['evidence'][0]['kind']='issuer'
        req['evidence'][0]['uri']='test-fixture://not-real-research'
        return req
    def factual(self, state, sid='mandate'):
        art=self.art(state,sid);ev=state['frozen']['request']['evidence'][0];metric=ev['metrics'][0]
        art['producer']={'name':'TEST FIXTURE analyst','type':'human' if state['frozen']['request']['mode']=='research' else 'synthetic'}
        art['claims'].append({'id':'F1','kind':'FACT','text':'TEST FIXTURE metric only.','scope':metric['scope'],'period':metric['period'],'evidence_ids':[ev['id']],
            'metric':{'evidence_id':ev['id'],'metric_id':metric['id'],'value':metric['value'],'unit':metric['unit']},'limitations':['This is a synthetic regression test, not a real finding.']})
        return art
    def full_research_fixture(self):
        req=self.research_request();state=self.start(req)
        while engine.ready(state):
            sid=engine.ready(state)[0]
            art=self.factual(state,sid)
            state=engine.submit(self.base/'run',sid,art,state['revision'])
        return state
    def public_fixture(self):
        req=self.research_request();inst=req['instruments'][0];inst['market_access']='public'
        ev={'id':'QUOTE','title':'TEST QUOTE','publisher':'Test publisher','uri':'test://quote','locator':'test fixture',
            'kind':'market','review_status':'REVIEWED','scope':[inst['id']],'observed_on':req['as_of'],'available_on':req['as_of'],'retrieved_on':req['as_of'],
            'metrics':[{'id':'price','value':99.5,'unit':inst['currency'],'period':req['as_of'],'scope':inst['id']}]}
        req['evidence'].append(ev)
        state={'frozen':{'request':req,'config':self.cfg,'stages':self.cfg['stages']},'run_id':'test','input_digest':'test'}
        expression=self.art(state,'expression')['investment_expression'];expression['status']='PUBLIC_MARKET_CANDIDATE'
        expression['checks']={k:'PASS' for k in expression['checks']}
        expression['quotes']=[{'instrument_id':inst['id'],'evidence_id':'QUOTE','metric_id':'price','quote_type':'INDICATIVE','price_convention':'test dirty price in stated currency per stated unit','timestamp_with_timezone':req['as_of']+'T12:00:00+00:00'}]
        return req,expression,{e['id']:e for e in req['evidence']}

    def test_valid_request(self): validate_request(self.request,self.cfg)
    def test_all_routes_end_to_end(self):
        for route in self.cfg['routes']:
            with self.subTest(route=route):
                s=run_demo(self.base/route,route)
                self.assertEqual(engine.status(s)['status'],'SYNTHETIC_COMPLETE_NOT_APPROVED')
                self.assertEqual(len(s['artifacts']),len(self.cfg['routes'][route]['nodes']))
                self.assertFalse(engine.status(s)['execution_authorized'])
    def test_source_study_stops(self):
        state=run_source_study(self.base/'study')
        self.assertEqual(engine.status(state)['status'],'NEEDS_DATA')
        self.assertEqual(len(state['artifacts']),2)
        self.assertTrue(engine.blockers(state))
    def test_unknown_route(self):
        self.request['route']='unknown'
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_wrong_instrument_type(self):
        self.request['instruments'][0]['asset_type']='unsupported'
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_future_request(self):
        self.request['as_of']=(date.today()+timedelta(days=1)).isoformat()
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_future_evidence(self):
        self.request['evidence'][0]['available_on']=(date.today()+timedelta(days=1)).isoformat()
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_invalid_calendar_date(self):
        self.request['as_of']='2026-02-30'
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_duplicate_evidence(self):
        self.request['evidence']*=2
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_duplicate_instrument(self):
        self.request['instruments']*=2
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_unknown_evidence_scope(self):
        self.request['evidence'][0]['scope']=['another-issuer']
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_metric_scope_mismatch(self):
        self.request['evidence'][0]['metrics'][0]['scope']='another-issuer'
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_nonfinite_source_metric(self):
        for value in (float('nan'),float('inf'),True):
            with self.subTest(value=value):
                self.request['evidence'][0]['metrics'][0]['value']=value
                with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_synthetic_cannot_enter_research(self):
        self.request['mode']='research'
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_bad_source_hash(self):
        self.request['evidence'][0]['content_sha256']='not-a-sha'
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_negative_freshness(self):
        self.request['freshness_policy']['market_max_age_days']=-1
        with self.assertRaises(DataError): validate_request(self.request,self.cfg)
    def test_json_duplicate_keys(self):
        p=self.base/'bad.json';p.write_text('{"id":1,"id":2}')
        with self.assertRaises(DataError): load_json(p)
    def test_json_nan(self):
        p=self.base/'bad.json';p.write_text('{"value":NaN}')
        with self.assertRaises(DataError): load_json(p)
    def test_dag_cycle(self):
        with self.assertRaises(DataError): validate_dag([{'id':'a','depends_on':['b']},{'id':'b','depends_on':['a']}])
    def test_dag_unknown_dependency(self):
        with self.assertRaises(DataError): validate_dag([{'id':'a','depends_on':['absent']}])
    def test_run_directory_not_overwritten(self):
        self.start()
        with self.assertRaises(DataError): self.start()
    def test_dependency_gate(self):
        state=self.start()
        with self.assertRaises(DataError): engine.submit(self.base/'run','evidence',self.art(state,'evidence'),0)
    def test_stale_submission_revision(self):
        state=self.start()
        with self.assertRaises(DataError): engine.submit(self.base/'run','mandate',self.art(state),1)
    def test_cross_run_artifact(self):
        state=self.start();art=self.art(state);art['run_id']='different'
        with self.assertRaises(DataError): engine.submit(self.base/'run','mandate',art,0)
    def test_wrong_input_digest(self):
        state=self.start();art=self.art(state);art['input_digest']='different'
        with self.assertRaises(DataError): engine.submit(self.base/'run','mandate',art,0)
    def test_replacement_archives_descendants(self):
        state=run_demo(self.base/'run');n=len(state['artifacts'])
        state=engine.submit(self.base/'run','mandate',self.art(state),state['revision'])
        self.assertEqual(set(state['artifacts']),{'mandate'});self.assertEqual(len(state['history']),n)
    def test_state_tamper_detected(self):
        state=self.start();state['revision']=200
        (self.base/'run/state.json').write_text(json.dumps(state))
        with self.assertRaises(DataError): engine.load_state(self.base/'run')
    def test_event_tamper_even_if_state_digest_updated(self):
        state=self.start();state['events'][0]['action']='CHANGED';engine.save(self.base/'run',state)
        with self.assertRaises(DataError): engine.load_state(self.base/'run')
    def test_runtime_change_detected(self):
        state=self.start();state['frozen']['runtime_files']={};state['input_digest']=engine.digest(state['frozen']);engine.save(self.base/'run',state)
        with self.assertRaises(DataError): engine.load_state(self.base/'run')
    def test_frozen_digest_tamper(self):
        state=self.start();state['frozen']['request']['subject']['name']='changed';engine.save(self.base/'run',state)
        with self.assertRaises(DataError): engine.load_state(self.base/'run')
    def test_writer_lock(self):
        state=self.start();(self.base/'run/.write.lock').write_text('test')
        with self.assertRaises(DataError): engine.submit(self.base/'run','mandate',self.art(state),0)
    def test_untrusted_inputs_are_labelled(self):
        packet=engine.packets(self.start())[0]
        self.assertIn('untrusted_request_and_evidence',packet);self.assertIn('trusted_operating_contract',packet)
    def test_incomplete_output_needs_explanation(self):
        state=self.start();art=self.art(state);art['status']='NEEDS_DATA'
        with self.assertRaises(DataError): self.validate(art,state)
    def test_complete_cannot_carry_material_gap(self):
        state=self.start();art=self.art(state);art['gaps']=['missing contract']
        with self.assertRaises(DataError): self.validate(art,state)
    def test_required_section_gate(self):
        state=self.start();art=self.art(state);art['sections']={}
        with self.assertRaises(DataError): self.validate(art,state)
    def test_section_claim_reference(self):
        state=self.start();art=self.art(state);next(iter(art['sections'].values()))['claim_ids']=['absent']
        with self.assertRaises(DataError): self.validate(art,state)
    def test_unreviewed_fact(self):
        self.request['evidence'][0]['review_status']='UNREVIEWED';state=self.start();art=self.factual(state)
        with self.assertRaises(DataError): self.validate(art,state)
    def test_unknown_claim_evidence(self):
        state=self.start();art=self.factual(state);art['claims'][-1]['evidence_ids']=['absent']
        with self.assertRaises(DataError): self.validate(art,state)
    def test_numerical_fact_unit(self):
        state=self.start();art=self.factual(state);art['claims'][-1]['metric']['unit']='millions USD'
        with self.assertRaises(DataError): self.validate(art,state)
    def test_numerical_fact_value(self):
        state=self.start();art=self.factual(state);art['claims'][-1]['metric']['value']=100000000
        with self.assertRaises(DataError): self.validate(art,state)
    def test_numerical_fact_period(self):
        state=self.start();art=self.factual(state);art['claims'][-1]['period']='wrong year'
        with self.assertRaises(DataError): self.validate(art,state)
    def test_calculation_recomputed(self):
        state=self.start();art=self.art(state);c=calculation_record('dscr',{'cash_available':100,'debt_service':50});c['result']=3;art['calculations']=[c]
        with self.assertRaises(DataError): self.validate(art,state)
    def test_calculation_input_unit(self):
        state=self.start();art=self.art(state);c=calculation_record('dscr',{'cash_available':100,'debt_service':50});c['input_provenance']['cash_available']['unit']='EUR';art['calculations']=[c]
        with self.assertRaises(DataError): self.validate(art,state)
    def test_calculation_output_unit(self):
        state=self.start();art=self.art(state);c=calculation_record('dscr',{'cash_available':100,'debt_service':50});c['output_unit']='USD';art['calculations']=[c]
        with self.assertRaises(DataError): self.validate(art,state)
    def test_missing_calculation_provenance(self):
        state=self.start();art=self.art(state);c=calculation_record('dscr',{'cash_available':100,'debt_service':50});c['input_provenance']={};art['calculations']=[c]
        with self.assertRaises(DataError): self.validate(art,state)
    def test_unknown_calculation_operation(self):
        state=self.start();art=self.art(state);c=calculation_record('dscr',{'cash_available':100,'debt_service':50});c['operation']='eval';art['calculations']=[c]
        with self.assertRaises(DataError): self.validate(art,state)
    def test_valid_source_bound_calculation(self):
        state=self.start();art=self.art(state);c=calculation_record('dscr',{'cash_available':100,'debt_service':50})
        c['input_provenance']['cash_available']={'evidence_id':'SYN-1','metric_id':'fixture-value','unit':'USD'};art['calculations']=[c]
        self.validate(art,state)
    def test_explicit_conversion(self):
        state=self.start();art=self.art(state);art['calculations']=[calculation_record('scale',{'value':5,'factor':.01},input_unit='percent',result_unit='decimal')]
        self.validate(art,state);self.assertEqual(art['calculations'][0]['result'],.05)
    def test_missing_standard_review(self):
        state=self.start();sid=next(s for s in state['frozen']['stages'] if state['frozen']['stages'][s]['standard_ids']);art=self.art(state,sid);art['standards_considered']=[]
        with self.assertRaises(DataError): self.validate(art,state,sid)
    def test_future_or_voluntary_reference_not_current_law(self):
        state=self.start();art=self.art(state);standard=self.standards[0]
        art['standards_considered']=[standard['id']]
        art['claims'].append({'id':'METHOD','kind':'METHOD','text':'Invalid law assertion for testing.','scope':'methodology','period':self.request['as_of'],'evidence_ids':[],'limitations':[],'standard_id':standard['id'],'applied_as_current_rule':True})
        with self.assertRaises(DataError): self.validate(art,state)
    def test_confidence_range(self):
        state=self.start();art=self.art(state);art['confidence']['value']=1.1
        with self.assertRaises(DataError): self.validate(art,state)
    def test_public_candidate_valid_typed_fixture(self):
        req,expression,evidence=self.public_fixture();validate_expression(expression,req,evidence)
    def test_public_candidate_missing_quote(self):
        req,expression,evidence=self.public_fixture();expression['quotes']=[]
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_public_candidate_stale_quote(self):
        req,expression,evidence=self.public_fixture();old=(date.fromisoformat(req['as_of'])-timedelta(days=2)).isoformat();evidence['QUOTE']['observed_on']=old
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_public_candidate_wrong_instrument_quote(self):
        req,expression,evidence=self.public_fixture();evidence['QUOTE']['scope']=[req['subject']['id']]
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_public_candidate_unknown_eligibility(self):
        req,expression,evidence=self.public_fixture();expression['checks']['liquidity']='UNKNOWN'
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_quote_timezone_required(self):
        req,expression,evidence=self.public_fixture();expression['quotes'][0]['timestamp_with_timezone']=req['as_of']+'T12:00:00'
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_synthetic_never_candidate(self):
        req,expression,evidence=self.public_fixture();req['mode']='synthetic'
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_no_execution_authority(self):
        req,expression,evidence=self.public_fixture();expression['execution_authorized']=True
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_private_candidate_needs_contract(self):
        req,expression,evidence=self.public_fixture();req['instruments'][0]['market_access']='private';expression['status']='PRIVATE_MARKET_CANDIDATE';expression['contract_evidence_ids']=[]
        with self.assertRaises(DataError): validate_expression(expression,req,evidence)
    def test_private_candidate_typed_contract(self):
        req,expression,evidence=self.public_fixture();inst=req['instruments'][0];inst['market_access']='private';expression['status']='PRIVATE_MARKET_CANDIDATE'
        evidence['CONTRACT']={'kind':'contract','review_status':'REVIEWED','scope':[inst['id']]};expression['contract_evidence_ids']=['CONTRACT']
        validate_expression(expression,req,evidence)
    def test_synthetic_review_rejected(self):
        state=run_demo(self.base/'run')
        with self.assertRaises(DataError): engine.review(self.base/'run','Human','APPROVE_RESEARCH','Test',state['revision'],True)
    def test_source_study_review_rejected(self):
        state=run_source_study(self.base/'study')
        with self.assertRaises(DataError): engine.review(self.base/'study','Human','APPROVE_RESEARCH','Test',state['revision'],True)
    def test_human_attestation_required(self):
        state=self.full_research_fixture()
        with self.assertRaises(DataError): engine.review(self.base/'run','Human','APPROVE_RESEARCH','Test',state['revision'],False)
    def test_research_approval_and_revision_invalidation(self):
        state=self.full_research_fixture();state=engine.review(self.base/'run','TEST human','APPROVE_RESEARCH','Synthetic test of gate only',state['revision'],True)
        self.assertEqual(engine.status(state)['status'],'RESEARCH_APPROVED');self.assertFalse(state['review']['execution_authorized'])
        state=engine.submit(self.base/'run','mandate',self.factual(state),state['revision'])
        self.assertIsNone(state['review']);self.assertEqual(len(state['review_history']),1)
    def test_material_issue_anywhere_blocks(self):
        state=self.full_research_fixture();art=copy.deepcopy(state['artifacts']['memo']);art['issues']=[{'id':'open','status':'OPEN','severity':'MATERIAL','description':'Missing independent outcome evidence.'}]
        state=engine.submit(self.base/'run','memo',art,state['revision'])
        self.assertEqual(engine.status(state)['status'],'BLOCKED_FOR_REVIEW')
        with self.assertRaises(DataError): engine.review(self.base/'run','Human','APPROVE_RESEARCH','Test',state['revision'],True)
    def test_reject_incomplete_research_allowed(self):
        state=self.start(self.research_request());state=engine.review(self.base/'run','Human','REJECT_RESEARCH','Insufficient evidence',0,True)
        self.assertEqual(engine.status(state)['status'],'RESEARCH_REJECTED')
    def test_stale_review_revision(self):
        state=self.full_research_fixture()
        with self.assertRaises(DataError): engine.review(self.base/'run','Human','APPROVE_RESEARCH','Test',state['revision']-1,True)
    def test_stale_standard_blocks(self):
        state=self.full_research_fixture();sid=next(iter({s for a in state['artifacts'].values() for s in a['standards_considered']}))
        item=next(s for s in state['frozen']['standards'] if s['id']==sid);item['checked_on']='2020-01-01'
        self.assertTrue(any(sid in message for message in engine.blockers(state)))
    def test_csv_formula_prefix(self):
        for value in ('=1+1','+cmd','-2+3','@SUM(1)','  =1'):
            self.assertTrue(engine.safe_cell(value).startswith("'"))
    def test_export_files_and_no_overwrite(self):
        run_demo(self.base/'run');files=engine.export(self.base/'run',self.base/'export')
        self.assertEqual(set(files),{'claims.csv','evidence.csv','research-packet.md','research-packet.json'})
        self.assertIn('NOT INVESTMENT RESEARCH APPROVED',(self.base/'export/research-packet.md').read_text())
        with self.assertRaises(DataError): engine.export(self.base/'run',self.base/'export')

if __name__=='__main__': unittest.main()
