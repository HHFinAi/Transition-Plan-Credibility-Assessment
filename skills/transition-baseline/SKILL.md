---
name: transition-baseline
description: Emissions baseline and comparability for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Emissions baseline and comparability

Read `../../AGENTS.md` and `../../prompts/stages/baseline.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Reconcile Scope 1, Scope 2 method and material Scope 3 categories; distinguish physical changes, M&A, disposal, outsourcing and restatements. Do not net offsets or avoided emissions against gross corporate emissions.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: scopes_boundaries, base_year_restatements, absolute_vs_intensity, offsets_separate. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.
