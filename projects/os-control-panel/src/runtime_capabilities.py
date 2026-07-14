from __future__ import annotations

import os

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
WEB_APP_FRONTEND_BUNDLE_ROOT = REPO_ROOT / "agent" / "capabilities" / "web-app-frontend"
API_AGENTS_ENABLED_ENV = "AI_BUILDER_OS_ENABLE_API_AGENTS"


@dataclass(frozen=True)
class CapabilityDoc:
    key: str
    title: str
    filename: str
    summary: str

    @property
    def path(self) -> Path:
        return WEB_APP_FRONTEND_BUNDLE_ROOT / self.filename


WEB_APP_FRONTEND_DOCS: tuple[CapabilityDoc, ...] = (
    CapabilityDoc(
        key="frontend_app_builder",
        title="Frontend app builder",
        filename="frontend-app-builder.md",
        summary="Browser-native app structure, reusable UI sections, responsive layout, and real user-facing states.",
    ),
    CapabilityDoc(
        key="frontend_testing_debugging",
        title="Frontend testing and debugging",
        filename="frontend-testing-debugging.md",
        summary="Rendered-surface verification, responsive checks, and interaction-state debugging.",
    ),
    CapabilityDoc(
        key="react_best_practices",
        title="React best practices",
        filename="react-best-practices.md",
        summary="Clear component boundaries, reusable patterns, and maintainable interaction state.",
    ),
    CapabilityDoc(
        key="shadcn_best_practices",
        title="shadcn/ui best practices",
        filename="shadcn-best-practices.md",
        summary="Composable component-system guidance for hierarchy, forms, actions, and consistency.",
    ),
)


def web_app_frontend_bundle_installed() -> bool:
    return WEB_APP_FRONTEND_BUNDLE_ROOT.exists() and all(doc.path.exists() for doc in WEB_APP_FRONTEND_DOCS)


def web_app_frontend_bundle_summary() -> str:
    lines = [
        "Local capability bundle: web-app-frontend",
        "Included docs:",
    ]
    for doc in WEB_APP_FRONTEND_DOCS:
        lines.append(f"- {doc.title}: {doc.summary}")
        lines.append(f"  Path: {doc.path.relative_to(REPO_ROOT)}")
    lines.append("Boundary:")
    lines.append("- Excludes Stripe, database, auth-provider, and broad backend capability from this first slice.")
    return "\n".join(lines)


def api_agents_enabled() -> bool:
    """Return whether the optional API-billed model runtime is enabled for Streamlit live flows."""
    return os.getenv(API_AGENTS_ENABLED_ENV, "").strip().lower() in {"1", "true", "yes", "on"}
