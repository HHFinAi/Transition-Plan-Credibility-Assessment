# Methodology and model boundaries

Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.

## Analytical outputs
- Target and boundary reconciliation
- Funded capex and technology-dependency assessment
- Absolute/intensity/activity bridge
- Delivery milestones and valuation handoff

## Calculation library
The implementation is in `sf_agent/analytics.py`; generic helpers are in `sf_agent/maths.py`. Every exposed operation has argument-unit and result-unit metadata and is callable with `python -m sf_agent calc`. Arguments are not sourced automatically. See the operation inventory below, the worked example and domain regression tests.

### Transition calculations
`target_path` assumes a strictly positive absolute-emissions target below or equal to the baseline and a constant compound rate between integer years. It reports required annual decline, an illustrative path and the observed gap. A zero net-zero endpoint must not be forced through a compound exponential: the helper rejects it. Target alignment and delivery probability require separate expert analysis.

`activity_intensity_bridge` exactly reconciles E=A×I with symmetric effects ΔA×(I0+I1)/2 and ΔI×(A0+A1)/2. Lower intensity does not imply lower absolute emissions. Comparable boundaries, restatements and activity units must be reviewed. `capex_alignment_bounds` separates verified aligned capex, unassessed capex and the residual; it does not classify capex automatically. `funding_gap` reports max(required−committed,0), without assuming financing is available. SBTi target publication, issuer validation and the opening of V2.0 validation are distinct events.


## Evidence status
Causal and legal interpretations remain human judgments. The software is not a complete implementation or certification of the referenced standards. Read the exact applicable original documents; the dated source register gives the verification scope. Proposed changes and future validation dates must not be applied retrospectively or represented as current law.
