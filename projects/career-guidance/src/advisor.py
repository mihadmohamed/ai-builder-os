from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class SkillSignal:
    name: str
    keywords: tuple[str, ...]
    importance: str
    action: str
    resource: str


SKILL_SIGNALS: tuple[SkillSignal, ...] = (
    SkillSignal(
        name="Python data analysis",
        keywords=("python", "pandas", "numpy", "data analysis", "jupyter"),
        importance="High",
        action="Build a small portfolio project that cleans, analyses, and explains a real dataset in Python.",
        resource="Python for Everybody or Kaggle Learn Python and Pandas",
    ),
    SkillSignal(
        name="SQL and database querying",
        keywords=("sql", "postgres", "mysql", "database", "queries", "relational"),
        importance="High",
        action="Practise joins, aggregations, window functions, and write a short case study using sample business data.",
        resource="Mode SQL Tutorial or SQLBolt",
    ),
    SkillSignal(
        name="Dashboarding and business intelligence",
        keywords=("tableau", "power bi", "dashboard", "visualisation", "visualization", "bi"),
        importance="Medium",
        action="Create one dashboard that tracks a target business metric and explains the decisions it supports.",
        resource="Microsoft Power BI Guided Learning or Tableau Training videos",
    ),
    SkillSignal(
        name="Machine learning fundamentals",
        keywords=("machine learning", "scikit", "classification", "regression", "model", "predictive"),
        importance="Medium",
        action="Complete one supervised-learning project and document model choice, evaluation, and limitations.",
        resource="Google Machine Learning Crash Course or Kaggle Intro to Machine Learning",
    ),
    SkillSignal(
        name="Cloud deployment basics",
        keywords=("aws", "azure", "gcp", "cloud", "deployment", "docker"),
        importance="Medium",
        action="Deploy a small app or notebook-backed service and document the runtime, data, and monitoring choices.",
        resource="AWS Skill Builder Cloud Practitioner Essentials or Microsoft Learn Azure Fundamentals",
    ),
    SkillSignal(
        name="Stakeholder communication",
        keywords=("stakeholder", "presentation", "communicate", "storytelling", "executive", "client"),
        importance="Medium",
        action="Prepare a one-page decision memo and five-slide presentation for a recent analysis project.",
        resource="Data storytelling practice from Storytelling with Data",
    ),
    SkillSignal(
        name="Experimentation and metrics",
        keywords=("a/b", "experiment", "hypothesis", "metrics", "kpi", "statistical"),
        importance="Medium",
        action="Write an experiment plan with a hypothesis, success metric, sample considerations, and decision rule.",
        resource="Udacity A/B Testing notes or Optimizely experimentation glossary",
    ),
    SkillSignal(
        name="Project delivery methods",
        keywords=("agile", "scrum", "roadmap", "delivery", "sprint", "prioritisation", "prioritization"),
        importance="Medium",
        action="Map one previous project into milestones, trade-offs, risks, and measurable delivery outcomes.",
        resource="Atlassian Agile Coach",
    ),
)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_keyword(text: str, keyword: str) -> bool:
    escaped = re.escape(keyword.lower())
    if re.search(r"[a-z0-9]$", keyword.lower()):
        return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text) is not None
    return escaped in text


def _matched_keywords(text: str, signal: SkillSignal) -> list[str]:
    return [keyword for keyword in signal.keywords if _contains_keyword(text, keyword)]


def _split_target_jobs(target_jobs: str) -> list[str]:
    chunks = [chunk.strip(" -\n\t") for chunk in re.split(r"(?m)\n{2,}|^-{2,}$", target_jobs)]
    return [chunk for chunk in chunks if chunk]


def _cv_evidence(cv_text: str, signal: SkillSignal) -> str:
    matches = _matched_keywords(_normalise(cv_text), signal)
    if matches:
        return f"Related CV signal found: {', '.join(matches)}."
    return f"No clear CV evidence found for {signal.name.lower()}."


def analyze_career_fit(cv_text: str, target_jobs: str) -> dict[str, Any]:
    cv = _normalise(cv_text)
    jobs = _normalise(target_jobs)
    job_sections = _split_target_jobs(target_jobs)

    if not cv or not jobs:
        return {
            "ready": False,
            "summary": "Add both CV text and target job descriptions to generate a gap analysis.",
            "gaps": [],
            "development_plan": [],
            "warnings": ["CV text and target job descriptions are both required."],
        }

    gaps: list[dict[str, Any]] = []
    matched_strengths: list[str] = []

    for signal in SKILL_SIGNALS:
        target_matches = _matched_keywords(jobs, signal)
        if not target_matches:
            continue

        cv_matches = _matched_keywords(cv, signal)
        if cv_matches:
            matched_strengths.append(signal.name)
            continue

        gaps.append(
            {
                "skill": signal.name,
                "importance": signal.importance,
                "target_job_evidence": f"Target role mentions: {', '.join(target_matches)}.",
                "cv_evidence": _cv_evidence(cv_text, signal),
                "recommended_action": signal.action,
                "recommended_resource": signal.resource,
            }
        )

    warnings: list[str] = []
    if len(gaps) < 3:
        warnings.append(
            "Fewer than 3 gaps were found because the target jobs did not contain enough unmatched skill signals."
        )

    summary = (
        f"Analyzed {len(job_sections) or 1} target job input"
        f"{'' if (len(job_sections) or 1) == 1 else 's'} and found {len(gaps)} gap"
        f"{'' if len(gaps) == 1 else 's'}."
    )
    if matched_strengths:
        summary += f" Existing CV strengths include: {', '.join(matched_strengths[:3])}."

    development_plan = [
        {
            "focus_area": gap["skill"],
            "next_step": gap["recommended_action"],
            "resource": gap["recommended_resource"],
        }
        for gap in gaps
    ]

    return {
        "ready": True,
        "summary": summary,
        "gaps": gaps,
        "development_plan": development_plan,
        "warnings": warnings,
    }


def format_gap_summary(result: dict[str, Any]) -> str:
    if not result.get("ready"):
        return result.get("summary", "Analysis is not ready.")
    gap_count = len(result.get("gaps", []))
    plan_count = len(result.get("development_plan", []))
    return f"{gap_count} skill gaps identified with {plan_count} development actions."
