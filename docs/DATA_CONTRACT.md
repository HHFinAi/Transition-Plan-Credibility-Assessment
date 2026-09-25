# Input and output contracts

Request schema: `schemas/request.schema.json`. Artifact schema: `schemas/artifact.schema.json`. The executable validator additionally checks cross-record semantics, provenance, dates, allowed operations, quote/contract scope and frozen stage requirements.

## Intake
Use the actual subject and instrument IDs consistently. Resolve placeholders before use. Declare mandate objective, horizon, currency, constraints, risk budget and jurisdiction. Register authorized source locators and evidence metrics with period, scope and unit. Use real observation/publication/retrieval dates; do not backdate review. Evidence is immutable within a run; create a new run for a changed register.

## Submission
Copy run_id/input_digest/stage_id from `next`; submit against its revision. Include producer, summary, claims, calculations, standards considered, named sections, gaps, issues and subjective confidence basis. COMPLETE requires substantive sections linked to claims. NEEDS_DATA/BLOCKED preserves missing dependencies. Every declared unresolved MATERIAL/CRITICAL issue blocks approval.

FACT requires reviewed scoped evidence. Numeric facts must match registered metrics. ASSUMPTION includes its basis. CALCULATION links to a recomputed record. METHOD links to a dated method reference, and must not assert a proposal or unverified standard as a current legal rule. INFERENCE must preserve source support and uncertainty.

## Unit conventions
Monetary arguments use a declared common currency and scale; no FX conversion is inferred. Rates are decimal fractions unless explicitly named basis points. Dates use ISO notation. Null means unknown/unavailable, not zero. Refer to `docs/METHODOLOGY.md` and calculation function docstrings for each domain's additional conventions.
