# Target architecture and applicability

## Decision context
Are the issuer’s targets supported by comparable emissions boundaries, funded implementation and observable delivery?

## Assignment
Identify baseline, target year, coverage, absolute/intensity basis and validation status with dates. Verify any issuer validation in an authorized source. Treat V2.0 as published, with validation planned for Q1 2027 as of the source review date. Retrieve the edition actually applicable to the issuer.

## Required output sections
- `target_register`: substantive analysis linked to claim IDs.
- `coverage_and_interims`: substantive analysis linked to claim IDs.
- `standard_version`: substantive analysis linked to claim IDs.
- `dependencies`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use IFRS-TRANSITION, SBTI-V2, SBTI-VALIDATION with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.
