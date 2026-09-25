"""CLI for local host-driven research. No network, model calls or trade API."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from . import engine
from .analytics import OPERATIONS
from .demo import run_demo, run_source_study, calculation_record
from .validation import DataError, load_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=engine.config()['title'] + ' — research only, no execution')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('routes', help='List supported routes')
    init = commands.add_parser('init', help='Create a new frozen research run')
    init.add_argument('--request', type=Path, required=True); init.add_argument('--out', type=Path, required=True)
    for command in ('next', 'status', 'report'):
        sub = commands.add_parser(command); sub.add_argument('--run', type=Path, required=True)
    sub = commands.add_parser('submit')
    sub.add_argument('--run', type=Path, required=True); sub.add_argument('--stage', required=True)
    sub.add_argument('--artifact', type=Path, required=True); sub.add_argument('--revision', type=int, required=True)
    sub = commands.add_parser('export')
    sub.add_argument('--run', type=Path, required=True); sub.add_argument('--out', type=Path, required=True)
    sub = commands.add_parser('review', help='Human attestation only; never grants trade authority')
    sub.add_argument('--run', type=Path, required=True); sub.add_argument('--reviewer', required=True)
    sub.add_argument('--decision', choices=['APPROVE_RESEARCH','REJECT_RESEARCH'], required=True)
    sub.add_argument('--rationale', required=True); sub.add_argument('--revision', type=int, required=True)
    sub.add_argument('--attest-human', action='store_true')
    sub = commands.add_parser('demo', help='Run deterministic fictional fixtures')
    sub.add_argument('--out', type=Path, required=True); sub.add_argument('--route')
    sub = commands.add_parser('source-study', help='Replay a bounded source-study; stops on material gaps')
    sub.add_argument('--out', type=Path, required=True)
    sub = commands.add_parser('calc', help='Recompute an allowlisted illustrative calculation')
    sub.add_argument('--operation', choices=sorted(OPERATIONS), required=True)
    sub.add_argument('--arguments', type=Path, required=True); sub.add_argument('--currency', default='USD')
    sub.add_argument('--measurement-unit', default='specified_outcome')
    sub.add_argument('--input-unit', default='percent'); sub.add_argument('--result-unit', default='decimal')
    args = parser.parse_args(argv)
    try:
        if args.command == 'routes':
            result = {name: {'asset_types': r['asset_types'], 'stages': len(r['nodes'])} for name, r in engine.config()['routes'].items()}
        elif args.command == 'init':
            result = engine.status(engine.start(load_json(args.request), args.out))
        elif args.command == 'demo':
            result = engine.status(run_demo(args.out, args.route))
        elif args.command == 'source-study':
            result = engine.status(run_source_study(args.out))
        elif args.command == 'calc':
            result = calculation_record(args.operation, load_json(args.arguments), currency=args.currency,
                measurement_unit=args.measurement_unit, input_unit=args.input_unit, result_unit=args.result_unit)
        elif args.command == 'submit':
            result = engine.status(engine.submit(args.run, args.stage, load_json(args.artifact), args.revision))
        elif args.command == 'review':
            result = engine.status(engine.review(args.run, args.reviewer, args.decision, args.rationale,
                                 expected_revision=args.revision, attest_human=args.attest_human))
        elif args.command == 'export':
            result = engine.export(args.run, args.out)
        else:
            state = engine.load_state(args.run)
            if args.command == 'report':
                print(engine.report(state), end=''); return 0
            result = engine.packets(state) if args.command == 'next' else engine.status(state)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (DataError, OSError, KeyError, TypeError, ValueError, OverflowError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
