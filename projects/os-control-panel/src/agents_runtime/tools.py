from __future__ import annotations

import json
import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

from agents import RunContextWrapper, function_tool

from control_plane import WorkflowController

from .support import execute_context_tool


RuntimeContext = dict[str, Any]


def _project(context: RunContextWrapper[RuntimeContext]) -> str:
    project_name = str(context.context.get("project_name", "")).strip()
    if not project_name:
        raise ValueError("The agent run has no project_name context")
    return project_name


def _role(context: RunContextWrapper[RuntimeContext]) -> str:
    return str(context.context.get("active_role") or context.context.get("role") or "Orchestrator")


def _context_tool(
    context: RunContextWrapper[RuntimeContext],
    name: str,
    user_content: str = "",
    *,
    approval_granted: bool = False,
) -> str:
    messages = [{"role": "user", "content": user_content}] if user_content else []
    return execute_context_tool(
        _role(context),
        _project(context),
        name,
        messages=messages,
        approval_granted=approval_granted,
    )


def _validate_public_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("A public http(s) URL is required")
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Local URLs are not allowed")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        raise ValueError("The URL hostname could not be resolved") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError("Private, loopback, link-local, and reserved network addresses are not allowed")
    return url.strip()


@function_tool
def inspect_project(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read canonical requirements, tasks, approvals, and recent implementation state."""
    return json.dumps(WorkflowController().snapshot(_project(context)), sort_keys=True)


@function_tool
def get_deterministic_next_action(context: RunContextWrapper[RuntimeContext]) -> str:
    """Ask the deterministic controller which role and action must run next."""
    return json.dumps(WorkflowController().next_action(_project(context)).to_dict(), sort_keys=True)


@function_tool(needs_approval=True)
def record_product_intent(
    context: RunContextWrapper[RuntimeContext],
    intent: str,
    idempotency_key: str = "",
) -> str:
    """Record a concise, approved intent in canonical product history.

    Args:
        intent: Durable product intent, excluding private reasoning or raw chat transcripts.
        idempotency_key: Optional stable key that prevents duplicate history events.
    """
    event = WorkflowController().record_intent(
        _project(context),
        intent,
        actor=str(context.context.get("actor", "agents-sdk")),
        source=str(context.context.get("source", "agents-sdk")),
        idempotency_key=idempotency_key,
    )
    return json.dumps(event, sort_keys=True)


@function_tool
def inspect_product_history(context: RunContextWrapper[RuntimeContext], limit: int = 20) -> str:
    """Read recent canonical workflow events.

    Args:
        limit: Maximum number of recent events, from 1 through 100.
    """
    bounded = min(100, max(1, limit))
    return json.dumps(WorkflowController().history(_project(context), limit=bounded), sort_keys=True)


@function_tool
def read_project_summary(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read a bounded summary of durable product and active workflow state."""
    return _context_tool(context, "read_project_summary")


@function_tool
def read_requirements(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read canonical product requirements for the selected project."""
    return _context_tool(context, "read_requirements")


@function_tool
def read_tasks(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read canonical execution tasks for the selected project."""
    return _context_tool(context, "read_tasks")


@function_tool
def read_project_memory(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read durable project decisions and prior learning."""
    return _context_tool(context, "read_project_memory")


@function_tool
def read_project_rules(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read project-specific domain and operating rules."""
    return _context_tool(context, "read_project_rules")


@function_tool
def read_active_workflow(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read active approvals, clarifications, agent threads, findings, and implementation runs."""
    return _context_tool(context, "read_active_workflow")


@function_tool
def read_project_capability_profile(context: RunContextWrapper[RuntimeContext]) -> str:
    """Read runtime, design, OpenAI capability, and local capability decisions."""
    return _context_tool(context, "read_project_capability_profile")


@function_tool
def web_search(context: RunContextWrapper[RuntimeContext], query: str) -> str:
    """Search the public web for current grounded context.

    Args:
        query: Focused search query containing no secrets or personal data.
    """
    if not query.strip() or len(query) > 1000:
        raise ValueError("query must contain between 1 and 1000 characters")
    return _context_tool(context, "web_search", query.strip())


@function_tool
def fetch_webpage(context: RunContextWrapper[RuntimeContext], url: str) -> str:
    """Fetch and extract one public webpage.

    Args:
        url: Public http(s) URL; private and local networks are rejected.
    """
    return _context_tool(context, "fetch_webpage", _validate_public_url(url))


@function_tool
def crawl_website(context: RunContextWrapper[RuntimeContext], url: str) -> str:
    """Crawl a bounded set of pages on one public website.

    Args:
        url: Public http(s) starting URL; private and local networks are rejected.
    """
    return _context_tool(context, "crawl_website", _validate_public_url(url))


@function_tool
def render_webpage(context: RunContextWrapper[RuntimeContext], url: str) -> str:
    """Render a JavaScript-heavy public webpage and extract bounded content.

    Args:
        url: Public http(s) URL; private and local networks are rejected.
    """
    return _context_tool(context, "render_webpage", _validate_public_url(url))


@function_tool(needs_approval=True)
def download_site_images(context: RunContextWrapper[RuntimeContext], url: str) -> str:
    """Download bounded public website images into runtime-only storage after approval.

    Args:
        url: Public http(s) website URL; private and local networks are rejected.
    """
    return _context_tool(
        context,
        "download_site_images",
        _validate_public_url(url),
        approval_granted=True,
    )


@function_tool
def classify_downloaded_site_assets(context: RunContextWrapper[RuntimeContext], source_url: str) -> str:
    """Classify previously downloaded runtime-only website assets.

    Args:
        source_url: Original public website URL used for the download.
    """
    return _context_tool(context, "classify_downloaded_site_assets", _validate_public_url(source_url))


ROLE_CONTEXT_TOOLS = {
    "PM": [read_project_summary, read_requirements, read_tasks, read_project_memory, read_project_rules, read_active_workflow, read_project_capability_profile, web_search, fetch_webpage, crawl_website, render_webpage, download_site_images, classify_downloaded_site_assets],
    "Experience Designer": [read_project_summary, read_requirements, read_tasks, read_project_memory, read_project_rules, read_active_workflow, read_project_capability_profile, web_search, fetch_webpage, crawl_website, render_webpage, download_site_images, classify_downloaded_site_assets],
    "UI Designer": [read_project_summary, read_requirements, read_tasks, read_project_memory, read_project_rules, read_active_workflow, read_project_capability_profile, web_search, fetch_webpage, crawl_website, render_webpage, download_site_images, classify_downloaded_site_assets],
    "Learning Agent": [read_project_summary, read_requirements, read_tasks, read_project_memory, read_project_rules, read_active_workflow, read_project_capability_profile, web_search, fetch_webpage],
    "Orchestrator": [inspect_project, get_deterministic_next_action, inspect_product_history, read_project_summary, read_active_workflow, read_project_capability_profile],
    "Architect": [inspect_project, read_requirements, read_tasks, read_project_memory, read_project_rules, read_project_capability_profile],
    "Engineer": [inspect_project, get_deterministic_next_action, read_requirements, read_tasks, read_project_memory, read_project_rules, read_project_capability_profile],
    "QA": [inspect_project, read_requirements, read_tasks, read_project_rules, read_active_workflow, read_project_capability_profile],
}


def tools_for_role(role: str) -> list[Any]:
    """Return the explicit least-privilege SDK tool surface for a role."""
    return list(ROLE_CONTEXT_TOOLS.get(role, []))
