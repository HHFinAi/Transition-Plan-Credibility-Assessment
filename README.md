# Transition-Plan Credibility Assessment Agent

**Institutional-quality buy-side research, designed to support tradable investment decisions through a traceable, auditable workflow.**

Are the issuer’s targets supported by comparable emissions boundaries, funded implementation and observable delivery?

**HHFinAi · v0.2.0 · Python 3.10+ · 10 research stages · 3 named routes · Human review · No autonomous trading**

[Worked example](examples/WORKED_EXAMPLE.md) · [Workflow](WORKFLOW.md) · [Evidence and audit](docs/AUDIT.md) · [Controls and limits](docs/INSTITUTIONAL_QUALITY.md) · [Validation](docs/VALIDATION.md)

## What it delivers
- Target and boundary reconciliation
- Funded capex and technology-dependency assessment
- Absolute/intensity/activity bridge
- Delivery milestones and valuation handoff

## Run the tests and a synthetic demonstration
From the extracted repository root:
```bash
python -m unittest discover -s tests -v
python scripts/check_repository.py
python -m sf_agent routes
python -m sf_agent demo --out runs/demo-01
python -m sf_agent report --run runs/demo-01
python -m sf_agent export --run runs/demo-01 --out exports/demo-01
python -m sf_agent calc --operation target_path --arguments examples/calculation-arguments.json
```
Use `python3` where appropriate. Select a new output directory each time; existing runs are never overwritten. No external packages, model keys or network access are required. The synthetic demo uses fictional inputs and pre-authored fixtures. It does not perform live investment research.

## Perform an actual research workflow
Populate `examples/research-request-template.json` with verified identifiers, mandate and authorized source records; remove every placeholder. Keep it outside a public repository when confidential.
```bash
python -m sf_agent init --request your-request.json --out runs/research-01
python -m sf_agent next --run runs/research-01
# The host AI or human researches the ready stage and saves a structured artifact.
python -m sf_agent submit --run runs/research-01 --stage mandate --artifact your-artifact.json --revision 0
python -m sf_agent status --run runs/research-01
```
Repeat `next` and `submit` using the current revision. The engine validates and records research; it does not fetch documents or run an LLM. See [the host contract](AGENTS.md), [data contract](docs/DATA_CONTRACT.md), and [skills](PROMPTS.md). Missing material data require `NEEDS_DATA` or an explicit blocking issue.

## What institutional-quality, tradable and auditable mean here
**Institutional-quality** describes instrument-specific analysis, evidence, model assumptions, challenge and accountable review. **Tradable** means investment-decision relevance backed by scoped market or contract evidence, not a guarantee that a trade exists or should be executed. **Auditable** means local research records can be inspected and reconstructed—not tamper-proof storage, verified source truth or independent certification. Read the [claim-to-control map](docs/INSTITUTIONAL_QUALITY.md).

## Domain limits
Target validation does not establish financial attractiveness or future delivery. SBTi V2.0 publication and the opening of target validation are different events. Do not turn a credibility rubric into a probability of success.

## Source study and verification
The [bounded source-study packet](examples/reports/source-study-packet.md) uses a reviewed official-methodology reference and deliberately stops at NEEDS_DATA because methodology alone is not issuer evidence. The [synthetic packet](examples/reports/synthetic-packet.md) demonstrates structure only. Source references were checked within the scope recorded on **2026-09-25**; frameworks may change. [Sources and applicability](references/SOURCES.md).

## What does not run
No embedded AI model, live market feed, automatic extraction, scheduler, broker connection, external messaging or automatic voting. Human-review names are attestations, not authenticated identities. Tests establish selected software behavior—not alpha, comprehensive legal conformity, ecological validity, causal impact, complete data quality or production security. Runtime and host compatibility beyond the recorded tests are not certified.

## Repository and publication
[GitHub Desktop publication guide](START_HERE_GITHUB_DESKTOP.md) · [Prepared metadata](repository-metadata.json) · [GEO/SGO discoverability](docs/GEO_SEO.md) · [FAQ](docs/FAQ.md) · [Notices](NOTICE.md)

This is a locally prepared package for **HHFinAi**, not a claim of an already published repository. Preserve `.git` when integrating with existing work. All eight expansion packages use a shared versioned core, independently vendored to run offline. Old v0.1.0 repositories are not modified or silently upgraded. Use a new run after changing the runtime.
