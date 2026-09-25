# Progress and financial consequences

## Decision context
Are the issuer’s targets supported by comparable emissions boundaries, funded implementation and observable delivery?

## Assignment
Calculate required reduction and observed progress on comparable boundaries. Show the activity contribution separately from intensity improvement. Translate delays to explicit capex, cost or revenue sensitivities; do not present extrapolation as assured delivery.

## Required output sections
- `trajectory_gap`: substantive analysis linked to claim IDs.
- `activity_intensity_bridge`: substantive analysis linked to claim IDs.
- `cashflow_implications`: substantive analysis linked to claim IDs.
- `sensitivity`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use IFRS-TRANSITION with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.

A domain calculation must pass recomputation. The minimal runnable illustration is `target_path`; other needed specialist models must remain explicitly external and independently reviewed.
