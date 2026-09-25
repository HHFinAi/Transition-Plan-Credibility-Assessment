# Emissions baseline and comparability

## Decision context
Are the issuer’s targets supported by comparable emissions boundaries, funded implementation and observable delivery?

## Assignment
Reconcile Scope 1, Scope 2 method and material Scope 3 categories; distinguish physical changes, M&A, disposal, outsourcing and restatements. Do not net offsets or avoided emissions against gross corporate emissions.

## Required output sections
- `scopes_boundaries`: substantive analysis linked to claim IDs.
- `base_year_restatements`: substantive analysis linked to claim IDs.
- `absolute_vs_intensity`: substantive analysis linked to claim IDs.
- `offsets_separate`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use PCAF-2025 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.
