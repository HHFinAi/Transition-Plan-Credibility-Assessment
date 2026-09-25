"""Deterministic synthetic and bounded source-study examples, never live research."""
from __future__ import annotations
import copy
from pathlib import Path
from . import engine
from .analytics import OPERATIONS
from .validation import load_json, resolve_unit


def calculation_record(operation: str, arguments: dict, *, currency: str = 'USD', measurement_unit: str = 'specified_outcome', input_unit: str = 'percent', result_unit: str = 'decimal') -> dict:
    op = OPERATIONS[operation]
    record = {'id': 'C1', 'operation': operation, 'arguments': copy.deepcopy(arguments),
              'currency': currency, 'measurement_unit': measurement_unit, 'input_unit': input_unit,
              'result_unit': result_unit, 'input_provenance': {}, 'result': op(**arguments)}
    record['output_unit'] = resolve_unit(op.output_unit, record)
    for key in arguments:
        record['input_provenance'][key] = {'assumption': 'Explicit illustrative input, not a market observation or verified forecast.',
                                           'unit': resolve_unit(op.argument_units[key], record)}
    return record


def synthetic_request(route: str | None = None, root: Path = engine.ROOT) -> dict:
    cfg = engine.config(root)
    request = load_json(root / 'examples/synthetic-request.json')
    request['route'] = route or cfg['default_route']
    definition = cfg['routes'][request['route']]
    inst = request['instruments'][0]
    inst['asset_type'] = definition['asset_types'][0]
    inst['label'] = definition.get('required_label') or 'none'
    inst['market_access'] = 'not-investable'  # Fictional fixture; never imply market availability.
    return request


def fixture_artifact(state: dict, stage_id: str) -> dict:
    """Generate typed fixtures. This helper never represents model-generated research."""
    req = state['frozen']['request']
    cfg = state['frozen']['config']
    stage = state['frozen']['stages'][stage_id]
    assessment = cfg['demo_assessment']
    claim = {'id': 'A1', 'kind': 'ASSUMPTION', 'text': assessment,
             'basis': 'Original fictional fixture for workflow testing; not an observed investment result.',
             'scope': req['subject']['id'], 'period': req['as_of'], 'evidence_ids': [],
             'limitations': ['SYNTHETIC: all entity-level analysis below is illustrative.']}
    artifact = {'schema_version': '1.0', 'run_id': state['run_id'], 'input_digest': state['input_digest'],
                'stage_id': stage_id, 'status': 'COMPLETE',
                'producer': {'name': 'Deterministic synthetic fixture', 'type': 'synthetic'},
                'summary': f'SYNTHETIC — {stage["title"]}. No live documents or market feeds were used.',
                'claims': [claim], 'calculations': [], 'standards_considered': stage.get('standard_ids', []),
                'sections': {}, 'gaps': [], 'issues': [],
                'confidence': {'value': 0.0, 'basis': 'Not investment confidence; fixture has no empirical research validation.'}}
    for name in stage['required_sections']:
        artifact['sections'][name] = {'analysis': f'SYNTHETIC {name.replace("_", " ")}: {assessment} This fixture tests structured handoffs, not substantive completion of the live research checklist.', 'claim_ids': ['A1']}
    if stage.get('requires_calculation'):
        operation, arguments = cfg['demo_operation'], cfg['demo_arguments']
        if stage_id == 'fiscal':
            operation, arguments = 'swap_value', cfg['demo_arguments']
        calc = calculation_record(operation, arguments)
        artifact['calculations'] = [calc]
        artifact['claims'].append({'id': 'CALC1', 'kind': 'CALCULATION', 'text': f'Recomputed illustrative {operation}; inspect arguments, units and result in calculation C1.',
                                   'calculation_id': 'C1', 'scope': req['subject']['id'], 'period': req['as_of'], 'evidence_ids': [],
                                   'limitations': ['Bounded arithmetic under explicit fictional assumptions; not a live valuation.']})
        for section in artifact['sections'].values():
            section['claim_ids'].append('CALC1')
    if stage.get('investment_gate'):
        artifact['investment_expression'] = {'status': 'RESEARCH_ONLY', 'execution_authorized': False,
             'instrument_ids': [i['id'] for i in req['instruments']],
             'checks': {k: 'UNKNOWN' for k in ('mandate_fit','valuation','liquidity','downside','legal_access','portfolio_risk')},
             'valuation_basis': 'Illustrative arithmetic only; no current market data.',
             'entry_condition': 'Do not enter a position on a synthetic fixture.',
             'catalyst': 'No live catalyst verified; obtain a dated source before research use.',
             'downside': 'Unknown investment downside; all prices and cash flows require evidence.',
             'liquidity': 'Fictional instrument; no liquidity established.',
             'hedging': 'No hedge terms, borrow or funding evidence.',
             'thesis_breakers': 'Replace this entire fixture with reviewed issuer, instrument, outcome and market evidence.'}
    if stage.get("required_assessments"):
        artifact["domain_assessment"] = copy.deepcopy(cfg["demo_domain_assessment"])
    return artifact


def run_demo(directory: Path, route: str | None = None, root: Path = engine.ROOT) -> dict:
    state = engine.start(synthetic_request(route, root), directory, root)
    while engine.ready(state):
        sid = engine.ready(state)[0]
        state = engine.submit(directory, sid, fixture_artifact(state, sid), state['revision'], root)
    return state


def run_source_study(directory: Path, root: Path = engine.ROOT) -> dict:
    """Replay a pre-authored primary-source fact and deliberately stop on evidence gaps."""
    request = load_json(root / 'examples/source-study-request.json')
    case = load_json(root / 'examples/source-study-case.json')
    state = engine.start(request, directory, root)
    # Source-study only: the mandate is the declared bounded study request, not a trading mandate.
    first = fixture_artifact(state, 'mandate')
    first['producer'] = {'name': 'HHFinAi source-study replay; author-reviewed source excerpt', 'type': 'ai'}
    first['summary'] = 'Bounded primary-source methodology study; not live issuer diligence or investment approval.'
    first['claims'][0].update(text='The request is a historical document study with no trade authorization.',
                              basis='Explicit scope in the source-study request.', limitations=['Not a complete investment mandate.'])
    for section in first['sections'].values():
        section['analysis'] = 'Identify the methodology reference, record its version and scope, and request missing contractual, outcome and current market evidence. No investment recommendation is permitted.'
    state = engine.submit(directory, 'mandate', first, state['revision'], root)
    stage = state['frozen']['stages']['evidence']
    ev = request['evidence'][0]
    metric = ev.get('metrics', [])[0] if ev.get('metrics') else None
    fact = {'id': 'F1', 'kind': 'FACT', 'text': case['fact'],
            'scope': metric['scope'] if metric else ev['scope'][0],
            'period': metric['period'] if metric else ev['observed_on'],
            'evidence_ids': [ev['id']], 'limitations': case['limitations']}
    if metric:
        fact['metric'] = {'evidence_id': ev['id'], 'metric_id': metric['id'],
                          'value': metric['value'], 'unit': metric['unit']}
    artifact = {'schema_version': '1.0', 'run_id': state['run_id'], 'input_digest': state['input_digest'],
                'stage_id': 'evidence', 'status': 'NEEDS_DATA',
                'producer': {'name': 'HHFinAi bounded source-study replay', 'type': 'ai'},
                'summary': case['conclusion'], 'claims': [fact], 'calculations': [], 'standards_considered': stage['standard_ids'],
                'sections': {'source_register_review': {'analysis': case['fact'], 'claim_ids': ['F1']}},
                'gaps': case['gaps'], 'issues': [{'id': 'MISSING-DILIGENCE', 'severity': 'MATERIAL', 'status': 'OPEN', 'description': 'Methodology reference does not supply the full evidence needed for investment diligence.'}],
                'confidence': {'value': 0.8, 'basis': 'Subjective confidence in the bounded source identification only, not current financial attractiveness, legal validity or outcomes.'}}
    return engine.submit(directory, 'evidence', artifact, state['revision'], root)
