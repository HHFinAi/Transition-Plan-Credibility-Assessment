# Worked example — Transition-Plan Credibility Assessment Agent

**SYNTHETIC / RESEARCH_ONLY. All company, portfolio, instrument and outcome values are fictional. No capital should be deployed from this example.**

## Investment-relevant observation
Reducing gross absolute emissions from 1,000,000 to 500,000 tonnes over ten years requires an illustrative compound decline of approximately **6.70% annually**. The 2026 path is approximately **659,754 tonnes**; observed emissions of 750,000 leave a gap of approximately **90,246 tonnes**.

## Reproduce the arithmetic
From the repository root:
```bash
python -m sf_agent calc --operation target_path --arguments examples/calculation-arguments.json
```

### Inputs
```json
{
  "base_emissions": 1000000,
  "target_emissions": 500000,
  "base_year": 2020,
  "target_year": 2030,
  "observation_year": 2026,
  "observed_emissions": 750000
}
```

### Recomputed result
```json
{
  "required_compound_annual_reduction": 0.06696700846319259,
  "illustrative_path_emissions": 659753.9553864471,
  "gap_tco2e": 90246.04461355286,
  "observed_reduction_fraction": 0.25,
  "path_is_scenario_not_science_alignment": true
}
```

## What the result does not establish
A gap to an assumed geometric path is not a scientific-alignment verdict. Review boundaries, actual commissioning schedules, expenditure and sector pathways. Intensity improvement, announced targets and issuer validation are separate evidence questions.

## Diligence handoff
Fictional issuer: an absolute target and a funded implementation plan must be tested separately; a lower intensity need not mean lower absolute emissions.

Register source-backed inputs, contrary evidence, material data gaps and the investment constraints before replacing this illustrative result with actual research. Unit, boundary, timing, attribution and legal judgments are not supplied by arithmetic alone. No human research approval is recorded for this example.
