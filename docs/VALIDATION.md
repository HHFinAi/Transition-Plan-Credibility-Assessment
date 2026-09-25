# Executed validation — 0.2.0

Date: **25 September 2026**. Environment: Python **3.13.5**, **Linux**.

**119 local unit-test executions passed**, including **12 domain-specific tests**. Shared controls are intentionally rerun in every independently packaged repository; repeated controls do not represent independent financial-model validations. See [complete test log](TEST_LOG.txt) and [machine-readable record](validation.json).

**3 named routes** ran through their complete synthetic workflow, with status `SYNTHETIC_COMPLETE_NOT_APPROVED`. **39 request/artifact schema validations** passed. The bounded official-methodology study stopped at **NEEDS_DATA**. No synthetic or source-study packet was approved as investment research.

Tests cover selected arithmetic, finite numbers, evidence scopes/units/periods, calculation provenance/recomputation, required fields, domain declarations, stale revisions, dependency gating, material issues, review invalidation, local integrity checks, quote/contract gates and no execution authority. Domain test names and fixtures are inspectable in the `tests` folder.

## What was not established
No live issuer, portfolio or market diligence; no model-host integration test; no independent audit or penetration test; no exhaustive legal, PCAF, ICMA, IFRS, SBTi or other standards certification; no scientific or causal-impact validation; no alpha or tradability proof; no actual GitHub remote CI run. Local schema checks used the installed `jsonschema` library; runtime and unit tests need no third-party packages. Future dates/framework updates require revalidation.

The repository check validates local package structure, JSON, local Markdown links, source metadata, route definitions and shared runtime digests. It does not fetch remote URLs or authenticate external sources.
