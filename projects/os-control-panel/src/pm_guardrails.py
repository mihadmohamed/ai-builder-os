from __future__ import annotations

import re

from pm_contract import PMDecisionEnvelope, PMGuardrailFinding


REQUIRED_REQUIREMENT_SECTIONS = (
    "Problem statement",
    "Target user",
    "Core job-to-be-done",
    "Desired outcome",
    "Success and acceptance evidence",
    "Constraints",
    "Out of scope",
    "Assumptions",
    "Open questions",
)
COMPLETION_CLAIM_RE = re.compile(
    r"\b(?:i|we)\s+(?:have\s+)?(?:implemented|tested|released|deployed|completed|changed canonical)\b",
    re.I,
)
STATUS_CLAIM_RE = re.compile(r"\b(R\d+)\s+is\s+(NEW|BACKLOG|IN_PROGRESS|DONE)\b", re.I)


def _finding(severity: str, code: str, field: str, message: str, remediation: str) -> PMGuardrailFinding:
    return PMGuardrailFinding(
        severity=severity,  # type: ignore[arg-type]
        code=code,
        field=field,
        message=message,
        remediation=remediation,
    )


def collect_pm_guardrail_findings(project_name: str, decision: PMDecisionEnvelope) -> list[PMGuardrailFinding]:
    """Return stable structural findings without attempting subjective product scoring."""
    from workspace import load_requirement_document

    requirement_document = load_requirement_document(project_name)
    statuses = {
        item.id: item.status
        for item in requirement_document.active_requirements + requirement_document.backlog_requirements
    }
    findings: list[PMGuardrailFinding] = []

    for index, change in enumerate(decision.requirement_changes):
        description = change.description
        missing = [section for section in REQUIRED_REQUIREMENT_SECTIONS if f"{section}:" not in description]
        if missing:
            findings.append(_finding(
                "warning", "missing_requirement_sections", f"requirement_changes[{index}].description",
                f"Requirement {change.requirement_id or change.title} omits: {', '.join(missing)}.",
                "Add the missing decision sections or explain why they do not apply before approval.",
            ))
        success_match = re.search(
            r"Success(?: and acceptance evidence| criteria)?:\s*(.*?)(?:\n\n[A-Z][^\n]{1,60}:|\Z)",
            description,
            re.S,
        )
        if success_match is None or not re.search(r"(?m)^-\s+\S+", success_match.group(1)):
            findings.append(_finding(
                "warning", "non_testable_acceptance_evidence", f"requirement_changes[{index}].description",
                "Success evidence is missing or is not expressed as observable checks.",
                "Add outcome-focused bullet checks that a reviewer can verify.",
            ))
        prescription = re.search(r"\b(?:class|function|database table|endpoint|library|framework)\s+[`A-Za-z_]", description, re.I)
        if prescription:
            findings.append(_finding(
                "warning", "implementation_prescription", f"requirement_changes[{index}].description",
                "The requirement appears to prescribe an implementation mechanism.",
                "Move implementation choices to tasks unless the mechanism is a genuine product constraint.",
            ))

    if decision.facts and not decision.evidence:
        findings.append(_finding(
            "warning", "facts_without_evidence", "facts",
            "The proposal contains facts but no attributable evidence entries.",
            "Add first-party source references or label the claims as assumptions.",
        ))
    assumptions = {item.strip().casefold() for item in decision.assumptions if item.strip()}
    for fact in decision.facts:
        if fact.strip().casefold() in assumptions:
            findings.append(_finding(
                "blocking", "fact_assumption_conflict", "facts",
                f"The same claim appears as both fact and assumption: {fact.strip()}",
                "Classify the claim once and attach evidence if it is a fact.",
            ))
    for question in decision.open_questions:
        if decision.status == "READY_FOR_APPROVAL" and question.strip().casefold().startswith("blocking:"):
            findings.append(_finding(
                "blocking", "unresolved_blocking_ambiguity", "open_questions",
                question.strip(),
                "Return NEEDS_INPUT and resolve the blocking question before proposing canonical changes.",
            ))

    for fact in decision.facts:
        for requirement_id, claimed_status in STATUS_CLAIM_RE.findall(fact):
            actual = statuses.get(requirement_id.upper())
            if actual and actual != claimed_status.upper():
                findings.append(_finding(
                    "blocking", "invalid_canonical_state_claim", "facts",
                    f"{requirement_id.upper()} is {actual}, not {claimed_status.upper()}.",
                    "Refresh canonical state and revise the proposal.",
                ))
        if COMPLETION_CLAIM_RE.search(fact):
            findings.append(_finding(
                "blocking", "unsupported_completion_claim", "facts",
                "The PM claims it performed implementation, testing, release, or canonical mutation.",
                "Reference controller evidence and describe observed state without claiming PM execution.",
            ))

    for index, task in enumerate(decision.task_changes):
        if len(task.goal.strip()) < 15:
            findings.append(_finding(
                "warning", "vague_task_goal", f"task_changes[{index}].goal",
                "The task goal is too short to express a verifiable outcome.",
                "Describe the observable delivery outcome, not merely an activity.",
            ))
        if any(len(item.strip()) < 8 for item in task.validation):
            findings.append(_finding(
                "warning", "vague_task_validation", f"task_changes[{index}].validation",
                "One or more validation checks are too vague to be actionable.",
                "State the evidence or behavior that proves the task is complete.",
            ))

    return sorted(findings, key=lambda item: (item.severity != "blocking", item.code, item.field, item.message))
