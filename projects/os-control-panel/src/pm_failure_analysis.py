from __future__ import annotations

from collections import Counter
from typing import Any


FAILURE_CLASSES = {
    "instruction",
    "tool_policy",
    "live_contract",
    "fixture",
    "grader",
    "model_behavior",
}


def _primary_classification(
    *,
    case_id: str,
    dimension: str,
    failures: list[str],
    observation: dict[str, Any],
    contract: dict[str, Any],
    source_contract_version: str,
) -> tuple[str, str]:
    predates_successor = bool(source_contract_version) and (
        source_contract_version != str(contract.get("contract_version", ""))
    )
    fixture_cases = set(contract.get("fixture_backed_review_cases", []))
    if predates_successor and case_id in fixture_cases and dimension in {
        "typed_output",
        "approval_behavior",
        "trace_trajectory",
        "canonical_outcome",
    }:
        return (
            "fixture",
            "The v1 live adapter named a synthetic review target but the production evidence tool had no matching fixture.",
        )

    equivalences = contract.get("typed_output_equivalences", {}).get(case_id, {})
    if (
        predates_successor
        and
        dimension == "typed_output"
        and failures == ["unexpected_next_action"]
    ):
        observed = str(observation.get("typed_output", {}).get("next_action", ""))
        if observed in equivalences.get("next_action", []):
            return (
                "grader",
                "The observed hand-back action is contract-equivalent but the v1 grader accepted only one literal enum value.",
            )

    if dimension == "tool_choice" and any(value.startswith("unauthorized_tool:") for value in failures):
        return (
            "model_behavior",
            "The model selected a tool outside the active mode policy; the policy remains unchanged.",
        )
    if dimension == "consultations":
        return (
            "model_behavior",
            "The canonical PM contract required a material specialist consultation that the model omitted.",
        )
    if dimension == "tool_choice":
        return (
            "model_behavior",
            "The model omitted or misordered required canonical reads; the read policy remains unchanged.",
        )
    if dimension == "trace_trajectory":
        return (
            "model_behavior",
            "The observed trajectory missed a required event not attributable to the corrected review fixture.",
        )
    if dimension == "typed_output":
        if predates_successor and "unexpected_next_action" in failures:
            observed = str(observation.get("typed_output", {}).get("next_action", ""))
            if observed in equivalences.get("next_action", []):
                return (
                    "model_behavior",
                    "The hand-back enum is contract-equivalent, but the same dimension also contains an unchanged model-output failure.",
                )
        return (
            "model_behavior",
            "The model omitted a required typed field or returned a non-equivalent control value.",
        )
    return (
        "model_behavior",
        "The observed behavior did not meet the unchanged approved dimension contract.",
    )


def classify_campaign_failures(
    campaign: dict[str, Any],
    successor_contract: dict[str, Any],
) -> dict[str, Any]:
    """Classify privacy-safe grade failures without retaining model output or trace payloads."""
    records: list[dict[str, Any]] = []
    source_contract_version = str(
        campaign.get("manifest", {}).get("live_contract_version", "")
    )
    for attempt in campaign.get("attempts", []):
        if not isinstance(attempt, dict):
            continue
        grade = attempt.get("grade", {})
        observation = attempt.get("observation", {})
        if not isinstance(grade, dict) or not isinstance(observation, dict):
            continue
        for dimension_grade in grade.get("dimensions", []):
            if not isinstance(dimension_grade, dict) or dimension_grade.get("passed"):
                continue
            failures = [
                str(value)
                for value in dimension_grade.get("failures", [])
                if str(value).strip()
            ]
            primary, rationale = _primary_classification(
                case_id=str(attempt.get("case_id", "")),
                dimension=str(dimension_grade.get("dimension", "")),
                failures=failures,
                observation=observation,
                contract=successor_contract,
                source_contract_version=source_contract_version,
            )
            if primary not in FAILURE_CLASSES:
                raise ValueError(f"Unknown PM failure classification: {primary}")
            records.append(
                {
                    "candidate_id": str(attempt.get("candidate_id", "")),
                    "case_id": str(attempt.get("case_id", "")),
                    "dimension": str(dimension_grade.get("dimension", "")),
                    "failure_codes": failures,
                    "primary_classification": primary,
                    "rationale": rationale,
                }
            )

    counts = Counter(record["primary_classification"] for record in records)
    return {
        "schema_version": "2026-07-30.pm-sentinel-failure-matrix.v1",
        "batch_id": str(campaign.get("batch_id", "")),
        "records": records,
        "summary": {
            "failed_dimensions": len(records),
            "classifications": dict(sorted(counts.items())),
        },
        "privacy_boundary": (
            "Contains candidate IDs, case IDs, grade dimension names, failure codes, and deterministic "
            "classifications only; excludes raw model output, prompts, tool payloads, trace IDs, and secrets."
        ),
    }
