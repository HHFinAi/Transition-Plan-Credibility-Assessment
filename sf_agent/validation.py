"""Explicit data contracts; structural checks do not establish source truth."""
from __future__ import annotations
import json
import math
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

class DataError(ValueError):
    """Invalid, incomplete, stale, or unsupported research input."""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise DataError(message)

def text(value: Any, name: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{name}: non-empty text required")
    return value

def number(value: Any, name: str) -> float:
    require(isinstance(value, (float, int)) and not isinstance(value, bool), f"{name}: number required")
    require(math.isfinite(value), f"{name}: finite number required")
    return float(value)

def dated(value: Any, name: str) -> date:
    text(value, name)
    require(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)), f"{name}: ISO YYYY-MM-DD required")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise DataError(f"{name}: invalid date") from exc

def sequence(value: Any, name: str, nonempty: bool = False) -> list:
    require(isinstance(value, list), f"{name}: list required")
    if nonempty:
        require(bool(value), f"{name}: must not be empty")
    return value

def mapping(value: Any, name: str) -> dict:
    require(isinstance(value, dict), f"{name}: object required")
    return value

def load_json(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise DataError(f"JSON non-finite constant rejected: {value}")
    def unique_keys(pairs: list) -> dict:
        out = {}
        for key, value in pairs:
            require(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream, parse_constant=reject_constant, object_pairs_hook=unique_keys)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataError(f"Cannot read valid JSON from {path}: {exc}") from exc

def unique(items: list, field: str, name: str) -> None:
    keys = [text(mapping(item, name).get(field), f"{name}.{field}") for item in items]
    require(len(keys) == len(set(keys)), f"{name}: duplicate {field}")

def validate_dag(nodes: list[dict]) -> None:
    sequence(nodes, "nodes", True)
    unique(nodes, "id", "nodes")
    ids = {n["id"] for n in nodes}
    done = set()
    for node in nodes:
        deps = sequence(node.get("depends_on"), "depends_on")
        require(set(deps) <= ids, "unknown dependency")
        require(len(deps) == len(set(deps)), "duplicate dependency")
    while len(done) < len(ids):
        ready = {n["id"] for n in nodes if n["id"] not in done and set(n["depends_on"]) <= done}
        require(bool(ready), "workflow contains a cycle")
        done |= ready

def validate_request(req: dict, config: dict) -> None:
    mapping(req, "request")
    require(req.get("schema_version") == "1.0", "schema_version must be 1.0")
    require(req.get("mode") in {"research", "synthetic", "source-study"}, "invalid mode")
    as_of = dated(req.get("as_of"), "as_of")
    require(as_of <= date.today(), "as_of cannot be in the future")
    route = req.get("route")
    require(route in config["routes"], "unknown route")
    subject = mapping(req.get("subject"), "subject")
    for field in ("id", "name"):
        text(subject.get(field), f"subject.{field}")
    mandate = mapping(req.get("mandate"), "mandate")
    for field in ("objective", "base_currency", "horizon", "constraints", "risk_budget", "jurisdiction"):
        text(mandate.get(field), f"mandate.{field}")
    policy = mapping(req.get("freshness_policy"), "freshness_policy")
    for field in ("market_max_age_days", "standard_review_max_age_days"):
        require(type(policy.get(field)) is int and policy[field] >= 0, f"invalid freshness_policy.{field}")
    instruments = sequence(req.get("instruments"), "instruments")
    unique(instruments, "id", "instruments")
    for inst in instruments:
        for key in ("id", "name", "asset_type", "currency", "market_access"):
            text(inst.get(key), f"instrument.{key}")
        require(inst["asset_type"] in config["routes"][route]["asset_types"], "instrument type incompatible with route")
        require(inst["market_access"] in {"public", "private", "not-investable", "unknown"}, "invalid market_access")
        label = config["routes"][route].get("required_label")
        if label:
            require(inst.get("label") == label, "instrument sustainability label incompatible with route")
    known_scopes = {subject["id"]} | {i["id"] for i in instruments} | {"methodology"}
    evidence = sequence(req.get("evidence"), "evidence")
    unique(evidence, "id", "evidence")
    for ev in evidence:
        for field in ("id", "title", "publisher", "uri", "locator"):
            text(ev.get(field), f"evidence.{field}")
        require(ev.get("kind") in {"issuer", "instrument", "market", "ecological", "contract", "official", "methodology", "synthetic"}, "invalid evidence kind")
        require(ev.get("review_status") in {"REVIEWED", "UNREVIEWED", "CONFLICTED"}, "invalid evidence review status")
        if req["mode"] != "synthetic":
            require(ev["kind"] != "synthetic", "synthetic evidence cannot enter research/source-study")
        require(set(sequence(ev.get("scope"), "evidence.scope", True)) <= known_scopes, "unknown evidence scope")
        observation = dated(ev.get("observed_on"), "observed_on")
        available = dated(ev.get("available_on"), "available_on")
        retrieved = dated(ev.get("retrieved_on"), "retrieved_on")
        require(observation <= as_of and available <= as_of, "look-ahead evidence: observed/available after as_of")
        require(available <= retrieved <= date.today(), "retrieval date invalid")
        if ev.get("content_sha256"):
            require(bool(re.fullmatch(r"[0-9a-f]{64}", ev["content_sha256"])), "invalid source SHA-256")
        metrics = sequence(ev.get("metrics", []), "metrics")
        unique(metrics, "id", "metrics")
        for metric in metrics:
            number(metric.get("value"), "metric.value")
            for key in ("unit", "period", "scope"):
                text(metric.get(key), f"metric.{key}")
            require(metric["scope"] in ev["scope"], "metric scope outside evidence scope")
    validate_dag(config["routes"][route]["nodes"])

def close(actual: Any, expected: Any) -> bool:
    if type(actual) is bool or type(expected) is bool:
        return type(actual) is type(expected) and actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isfinite(actual) and math.isfinite(expected) and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(close(actual[k], expected[k]) for k in actual)
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(close(a, b) for a, b in zip(actual, expected))
    return actual == expected

def source_metric(evidence: dict, ev_id: str, metric_id: str) -> dict:
    require(ev_id in evidence, "unknown metric evidence id")
    metrics = {m["id"]: m for m in evidence[ev_id].get("metrics", [])}
    require(metric_id in metrics, "unknown source metric id")
    return metrics[metric_id]

def resolve_unit(unit: str, calculation: dict) -> str:
    """Resolve declared dimensions, never silently rescale an input."""
    if unit in {"$money", "money_per_outcome"}:
        currency = calculation.get("currency")
        require(isinstance(currency, str) and bool(re.fullmatch(r"[A-Z]{3}", currency)), "calculation currency: three uppercase letters required")
        if unit == "$money":
            return currency
        return currency + "/" + text(calculation.get("measurement_unit"), "measurement_unit")
    if unit == "$outcome":
        return text(calculation.get("measurement_unit"), "measurement_unit")
    if unit == "$input_unit":
        return text(calculation.get("input_unit"), "input_unit")
    if unit == "$output_unit":
        return text(calculation.get("result_unit"), "result_unit")
    return unit

def validate_artifact(artifact: dict, stage: dict, req: dict, standards: list, operations: dict) -> None:
    mapping(artifact, "artifact")
    require(artifact.get("schema_version") == "1.0", "artifact schema_version must be 1.0")
    require(artifact.get("stage_id") == stage["id"], "artifact stage mismatch")
    require(artifact.get("status") in {"COMPLETE", "NEEDS_DATA", "BLOCKED"}, "invalid artifact status")
    text(artifact.get("summary"), "summary")
    producer = mapping(artifact.get("producer"), "producer")
    text(producer.get("name"), "producer.name")
    require(producer.get("type") in {"human", "ai", "synthetic"}, "invalid producer type")
    if req["mode"] != "synthetic":
        require(producer["type"] != "synthetic", "synthetic producer cannot submit research")
    confidence = mapping(artifact.get("confidence"), "confidence")
    require(0 <= number(confidence.get("value"), "confidence.value") <= 1, "confidence outside [0,1]")
    text(confidence.get("basis"), "confidence.basis")
    issues = sequence(artifact.get("issues"), "issues")
    unique(issues, "id", "issues")
    for issue in issues:
        require(issue.get("severity") in {"MINOR", "MATERIAL", "CRITICAL"}, "invalid issue severity")
        require(issue.get("status") in {"OPEN", "RESOLVED"}, "invalid issue status")
        text(issue.get("description"), "issue.description")
        if issue["status"] == "RESOLVED":
            text(issue.get("resolution"), "resolved issue needs resolution")
    gaps = sequence(artifact.get("gaps"), "gaps")
    for gap in gaps:
        text(gap, "gap")
    if artifact["status"] in {"NEEDS_DATA", "BLOCKED"}:
        require(bool(gaps or issues), "noncomplete output must explain gaps/issues")
    else:
        require(not gaps, "COMPLETE artifact cannot carry undeclared unresolved gaps; use issue register for nonblocking limitations")
    evidence = {e["id"]: e for e in req["evidence"]}
    standard_map = {s["id"]: s for s in standards}
    considered = sequence(artifact.get("standards_considered"), "standards_considered")
    require(len(considered) == len(set(considered)) and set(considered) <= set(standard_map), "unknown/duplicate considered standard")
    if artifact["status"] == "COMPLETE":
        require(set(stage.get("standard_ids", [])) <= set(considered), "missing stage methodology review")
        require(all(dated(standard_map[s]["source_date"], "standard source_date") <= dated(req["as_of"], "as_of") for s in considered), "methodology postdates research as-of; select contemporaneous references")
    claims = sequence(artifact.get("claims"), "claims")
    unique(claims, "id", "claims")
    claim_map = {c["id"]: c for c in claims}
    for claim in claims:
        text(claim.get("text"), "claim.text")
        require(claim.get("kind") in {"FACT", "INFERENCE", "ASSUMPTION", "CALCULATION", "METHOD"}, "invalid claim kind")
        refs = sequence(claim.get("evidence_ids"), "claim.evidence_ids")
        require(set(refs) <= set(evidence), "unknown claim evidence id")
        text(claim.get("scope"), "claim.scope")
        require(claim["scope"] in {req["subject"]["id"], "methodology"} | {i["id"] for i in req["instruments"]}, "unknown claim scope")
        text(claim.get("period"), "claim.period")
        for limit in sequence(claim.get("limitations"), "claim.limitations"):
            text(limit, "claim limitation")
        if claim["kind"] in {"FACT", "INFERENCE"}:
            require(bool(refs), "fact/inference needs evidence")
            require(all(claim["scope"] in evidence[r]["scope"] for r in refs), "claim/evidence entity-boundary mismatch")
        if claim["kind"] == "FACT":
            require(all(evidence[r]["review_status"] == "REVIEWED" for r in refs), "fact relies on unreviewed/conflicted evidence")
            if req["mode"] == "research" and claim["scope"] != "methodology":
                require(any(evidence[r]["kind"] not in {"methodology", "synthetic"} for r in refs), "methodology does not prove issuer/instrument facts")
        if claim["kind"] == "ASSUMPTION":
            text(claim.get("basis"), "assumption basis")
        if claim["kind"] == "METHOD":
            sid = claim.get("standard_id")
            require(sid in standard_map and sid in considered, "unknown or unregistered methodology standard")
            if claim.get("applied_as_current_rule"):
                standard = standard_map[sid]
                require(standard.get("can_apply_as_current_rule") is True, "reference/future framework cannot be applied as a current rule")
                require(dated(standard["source_date"], "standard source_date") <= dated(req["as_of"], "as_of"), "look-ahead methodology")
        if "metric" in claim:
            metric = mapping(claim["metric"], "claim.metric")
            number(metric.get("value"), "claim.metric.value")
            text(metric.get("unit"), "claim.metric.unit")
            require(claim["kind"] == "FACT", "numeric source metric belongs to FACT; use calculation records for derived values")
            ev_id = metric.get("evidence_id")
            require(ev_id in refs, "numeric metric source missing from evidence_ids")
            original = source_metric(evidence, ev_id, metric.get("metric_id"))
            require(close(metric["value"], original["value"]), "reported metric value differs from source")
            require(metric["unit"] == original["unit"], "metric unit mismatch: conversions require explicit calculations")
            require(claim["period"] == original["period"] and claim["scope"] == original["scope"], "metric period/entity mismatch")
    calculations = sequence(artifact.get("calculations"), "calculations")
    unique(calculations, "id", "calculations")
    calc_map = {c["id"]: c for c in calculations}
    for claim in claims:
        if claim["kind"] == "CALCULATION":
            require(claim.get("calculation_id") in calc_map, "calculation claim has no calculation record")
    for calc in calculations:
        require(calc.get("operation") in operations, "calculation operation not allowlisted")
        op = operations[calc["operation"]]
        args = mapping(calc.get("arguments"), "calculation.arguments")
        require(set(args) == set(op.argument_units), "calculation arguments differ from operation contract")
        bindings = mapping(calc.get("input_provenance"), "calculation.input_provenance")
        require(set(bindings) == set(args), "every calculation argument requires provenance")
        for name, value in args.items():
            binding = mapping(bindings[name], "input provenance")
            require(binding.get("unit") == resolve_unit(op.argument_units[name], calc), "operation input unit mismatch; register an explicit conversion")
            if "assumption" in binding:
                text(binding["assumption"], "calculation assumption")
            else:
                original = source_metric(evidence, binding.get("evidence_id"), binding.get("metric_id"))
                require(evidence[binding["evidence_id"]]["review_status"] == "REVIEWED", "calculation input source unreviewed")
                require(close(value, original["value"]), "bound calculation input differs from source")
                require(binding.get("unit") == original["unit"], "calculation input unit mismatch")
        text(calc.get("output_unit"), "calculation.output_unit")
        require(calc["output_unit"] == resolve_unit(op.output_unit, calc), "operation output unit mismatch")
        try:
            recomputed = operations[calc["operation"]](**args)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
            raise DataError(f"invalid calculation arguments: {exc}") from exc
        require(close(calc.get("result"), recomputed), "calculation result failed independent recomputation")
    sections = mapping(artifact.get("sections"), "sections")
    if artifact["status"] == "COMPLETE":
        require(bool(claims), "COMPLETE needs claims")
        require(set(stage["required_sections"]) <= set(sections), "missing required analytical section")
    for key, section in sections.items():
        mapping(section, f"section.{key}")
        text(section.get("analysis"), f"section.{key}.analysis")
        ids = sequence(section.get("claim_ids"), "section.claim_ids", artifact["status"] == "COMPLETE")
        require(set(ids) <= set(claim_map), "section references unknown claim")
    if stage.get("requires_calculation") and artifact["status"] == "COMPLETE":
        require(bool(calculations), "valuation/economics stage needs a recomputed calculation; mark NEEDS_DATA when unavailable")
    if artifact["status"] == "COMPLETE" and stage.get("allowed_operations"):
        require(any(c["operation"] in stage["allowed_operations"] for c in calculations),
                "stage requires a domain-relevant calculation, not an unrelated operation")
    if artifact["status"] == "COMPLETE" and stage.get("required_assessments"):
        assessed = mapping(artifact.get("domain_assessment"), "domain_assessment")
        for field, choices in stage["required_assessments"].items():
            require(field in assessed, f"missing domain assessment: {field}")
            require(any(type(assessed[field]) is type(v) and assessed[field] == v for v in choices),
                    f"invalid domain assessment: {field}")
    if stage.get("investment_gate") and artifact["status"] == "COMPLETE":
        validate_expression(artifact.get("investment_expression"), req, evidence)

def validate_expression(expression: dict, req: dict, evidence: dict) -> None:
    mapping(expression, "investment_expression")
    status = expression.get("status")
    require(status in {"RESEARCH_ONLY", "PUBLIC_MARKET_CANDIDATE", "PRIVATE_MARKET_CANDIDATE", "NO_INVESTMENT_ROUTE"}, "invalid investment-expression status")
    require(expression.get("execution_authorized") is False, "research never authorizes execution")
    for field in ("valuation_basis", "entry_condition", "catalyst", "downside", "liquidity", "hedging", "thesis_breakers"):
        text(expression.get(field), f"investment_expression.{field}")
    ids = sequence(expression.get("instrument_ids"), "investment_expression.instrument_ids")
    instruments = {i["id"]: i for i in req["instruments"]}
    require(set(ids) <= set(instruments), "unknown investment instrument")
    checks = mapping(expression.get("checks"), "investment_expression.checks")
    required = {"mandate_fit", "valuation", "liquidity", "downside", "legal_access", "portfolio_risk"}
    require(required <= set(checks), "missing investment eligibility checks")
    require(all(v in {"PASS", "FAIL", "UNKNOWN"} for v in checks.values()), "invalid eligibility check")
    if status not in {"PUBLIC_MARKET_CANDIDATE", "PRIVATE_MARKET_CANDIDATE"}:
        return
    require(req["mode"] == "research", "demo/source-study cannot be marked an investment candidate")
    require(bool(ids), "investment candidate requires a specific instrument")
    require(all(checks[k] == "PASS" for k in required), "candidate requires all declared eligibility checks to pass")
    access = "public" if status == "PUBLIC_MARKET_CANDIDATE" else "private"
    require(all(instruments[i]["market_access"] == access for i in ids), "instrument market access does not support candidate status")
    if access == "public":
        quotes = sequence(expression.get("quotes"), "investment_expression.quotes", True)
        require({q.get("instrument_id") for q in quotes} == set(ids), "every public-market instrument needs a quote")
        for quote in quotes:
            ev = evidence.get(quote.get("evidence_id"), {})
            require(ev.get("kind") == "market" and ev.get("review_status") == "REVIEWED", "quote requires reviewed market evidence")
            require(quote["instrument_id"] in ev.get("scope", []), "quote is for the wrong instrument")
            age = (dated(req["as_of"], "as_of") - dated(ev["observed_on"], "market date")).days
            require(0 <= age <= req["freshness_policy"]["market_max_age_days"], "quote too stale for public-market candidate")
            metric = source_metric(evidence, quote["evidence_id"], quote.get("metric_id"))
            require(metric["scope"] == quote["instrument_id"] and metric["value"] > 0, "invalid quoted price metric")
            require(quote.get("quote_type") in {"INDICATIVE", "FIRM"}, "quote type must be disclosed")
            text(quote.get("price_convention"), "quote price_convention")
            stamp = text(quote.get("timestamp_with_timezone"), "quote timestamp_with_timezone")
            try:
                parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise DataError("quote timestamp is not ISO datetime") from exc
            require(parsed.tzinfo is not None and parsed.utcoffset() is not None, "quote timestamp requires timezone")
            require(parsed.date() == dated(ev["observed_on"], "market date"), "quote timestamp date differs from source observation date")
    else:
        contract_ids = sequence(expression.get("contract_evidence_ids"), "contract_evidence_ids", True)
        require(all(e in evidence and evidence[e]["kind"] == "contract" and evidence[e]["review_status"] == "REVIEWED" for e in contract_ids), "private candidate needs reviewed contract evidence")
        require(all(any(i in evidence[e]["scope"] for e in contract_ids) for i in ids), "missing private instrument contract")
