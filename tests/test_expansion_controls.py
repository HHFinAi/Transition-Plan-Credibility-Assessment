"""New v0.2.0 declarations and domain-calculation controls; synthetic test inputs."""
import copy,tempfile,unittest
from pathlib import Path
from sf_agent import engine
from sf_agent.analytics import OPERATIONS
from sf_agent.demo import fixture_artifact,synthetic_request,calculation_record
from sf_agent.validation import validate_artifact,load_json,DataError
class ExpansionControls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.s=engine.start(synthetic_request(),Path(self.temp.name)/'run')
    def tearDown(self):self.temp.cleanup()
    def validate(self,a,sid):
        validate_artifact(a,self.s['frozen']['stages'][sid],self.s['frozen']['request'],load_json(engine.ROOT/'references/standards.json')['standards'],OPERATIONS)
    def test_domain_assessment_required(self):
        a=fixture_artifact(self.s,'memo');a.pop('domain_assessment')
        with self.assertRaises(DataError):self.validate(a,'memo')
    def test_domain_assessment_field_required(self):
        a=fixture_artifact(self.s,'memo');a['domain_assessment'].pop(next(iter(a['domain_assessment'])))
        with self.assertRaises(DataError):self.validate(a,'memo')
    def test_domain_assessment_wrong_enum(self):
        a=fixture_artifact(self.s,'memo');a['domain_assessment'][next(iter(a['domain_assessment']))]='UNSAFE-UNRECOGNIZED'
        with self.assertRaises(DataError):self.validate(a,'memo')
    def test_domain_assessment_boolean_not_integer(self):
        a=fixture_artifact(self.s,'memo');k=next(k for k,v in a['domain_assessment'].items() if type(v)is bool);a['domain_assessment'][k]=int(a['domain_assessment'][k])
        with self.assertRaises(DataError):self.validate(a,'memo')
    def test_domain_assessment_valid_fixture(self):self.validate(fixture_artifact(self.s,'memo'),'memo')
    def test_unrelated_calculation_rejected(self):
        a=fixture_artifact(self.s,'valuation');a['calculations']=[calculation_record('dscr',{'cash_available':100,'debt_service':50})]
        with self.assertRaises(DataError):self.validate(a,'valuation')
    def test_domain_calculation_passes(self):self.validate(fixture_artifact(self.s,'valuation'),'valuation')
    def test_missing_data_does_not_require_domain_completion(self):
        a=fixture_artifact(self.s,'memo');a['status']='NEEDS_DATA';a['gaps']=['Missing scoped issuer records'];a.pop('domain_assessment');self.validate(a,'memo')
    def test_nonfinite_operation_result_rejected(self):
        with self.assertRaises(DataError):OPERATIONS['scale'](1e308,1e308)
    def test_nested_nonfinite_output_rejected(self):
        from sf_agent.maths import operation
        @operation({},'test')
        def bad_result():return {'nested':[float('inf')]}
        with self.assertRaises(DataError):bad_result()
    def test_no_conversion_of_unknown_to_zero(self):
        from sf_agent.maths import operation
        @operation({},'test')
        def nullable():return {'unknown':None,'observed':0,'flag':False}
        self.assertEqual(nullable(),{'unknown':None,'observed':0,'flag':False})
    def test_all_stage_sources_registered(self):
        registered={s['id'] for s in load_json(engine.ROOT/'references/standards.json')['standards']}
        for stage in engine.config()['stages'].values():self.assertLessEqual(set(stage['standard_ids']),registered)
    def test_all_domain_operations_allowed_for_valuation(self):
        self.assertIn(engine.config()['demo_operation'],engine.config()['stages']['valuation']['allowed_operations'])
if __name__=='__main__':unittest.main()
