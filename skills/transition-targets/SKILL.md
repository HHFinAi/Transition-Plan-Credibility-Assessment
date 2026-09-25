---
name: transition-targets
description: Target architecture and applicability for institutional sustainable-finance research; return evidence-linked findings, assumptions, gaps and reviewable outputs.
license: MIT
metadata:
  author: HHFinAi
  version: "0.2.0"
---
# Target architecture and applicability

Read `../../AGENTS.md` and `../../prompts/stages/targets.md` relative to this skill directory. Obtain the current stage packet using the repository CLI. Do not create or claim unavailable source access.

## Task
Identify baseline, target year, coverage, absolute/intensity basis and validation status with dates. Verify any issuer validation in an authorized source. Treat V2.0 as published, with validation planned for Q1 2027 as of the source review date. Retrieve the edition actually applicable to the issuer.

## Deliverable
Return the fields in `../../schemas/artifact.schema.json`; use the current run ID and input digest. Required sections: target_register, coverage_and_interims, standard_version, dependencies. Include source IDs, scope, periods, methods and material gaps. Call only allowlisted calculations with explicit provenance; missing evidence means NEEDS_DATA, not invented values.

## Limit
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.
