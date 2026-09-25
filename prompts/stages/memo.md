# Investment committee and accountable review

## Decision context
Are the issuer’s targets supported by comparable emissions boundaries, funded implementation and observable delivery?

## Assignment
Integrate findings without changing their qualification. Separate facts, inferences, assumptions and calculations; cite evidence IDs and dates. Preserve unknown conclusions. Complete the domain-assessment declarations, register unresolved material issues, and submit for human research review. Do not certify legal compliance or investment performance.

## Required output sections
- `investment_question_and_answer`: substantive analysis linked to claim IDs.
- `financial_vs_sustainability_conclusions`: substantive analysis linked to claim IDs.
- `evidence_and_calculations`: substantive analysis linked to claim IDs.
- `decision_conditions_and_limits`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use the mandate and registered primary evidence with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.

Required typed domain-assessment fields (declarations, not automated truth verification):
```json
{
  "target_basis": [
    "absolute",
    "intensity",
    "mixed",
    "unknown"
  ],
  "gross_emissions_separate": [
    true
  ],
  "boundary_review": [
    "comparable",
    "restated",
    "unresolved"
  ],
  "validation_status": [
    "validated_on_named_version",
    "not_validated",
    "not_verified"
  ],
  "publication_not_validation": [
    true
  ]
}
```
