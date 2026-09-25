# Implementation and capital allocation

## Decision context
Are the issuer’s targets supported by comparable emissions boundaries, funded implementation and observable delivery?

## Assignment
Tie projects to approved budget, commissioning schedule, procurement, operating changes and dependencies on grids, customers or suppliers. Separate announced, approved, funded and spent capex. Assess stranded-asset and execution risks without equating green-labelled capex with alignment.

## Required output sections
- `funded_capex`: substantive analysis linked to claim IDs.
- `technology_readiness`: substantive analysis linked to claim IDs.
- `operating_plan`: substantive analysis linked to claim IDs.
- `governance_and_incentives`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use IFRS-TRANSITION with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.
