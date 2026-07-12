from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from common import REPO_ROOT, PROJECTS_ROOT, normalize_project_directory_name


VIEWPORTS = (
    ("desktop", 1440, 1000),
    ("mobile", 390, 844),
)


def _wait_for_server(url: str, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # pragma: no cover - timing dependent
            last_error = exc
        time.sleep(0.5)
    detail = f": {last_error}" if last_error is not None else ""
    raise RuntimeError(f"Timed out waiting for {url}{detail}")


def _start_dev_server(project_dir: Path, port: int) -> subprocess.Popen[str]:
    return subprocess.Popen(
        ["npm", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", str(port)],
        cwd=project_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def _console_entry(message) -> dict[str, str]:
    return {
        "type": message.type,
        "text": message.text,
        "location": json.dumps(message.location),
    }


def _visible_targets(page) -> list[dict[str, str]]:
    return page.evaluate(
        """
        () => {
          const attribute = 'data-ai-builder-verify-id';
          for (const node of document.querySelectorAll(`[${attribute}]`)) {
            node.removeAttribute(attribute);
          }
          return Array.from(document.querySelectorAll('button, a[href]'))
            .filter((node) => {
              const rect = node.getBoundingClientRect();
              const style = window.getComputedStyle(node);
              return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
            })
            .slice(0, 8)
            .map((node, index) => {
              const verifyId = `target-${index}`;
              node.setAttribute(attribute, verifyId);
              return {
                verify_id: verifyId,
                tag: node.tagName.toLowerCase(),
                text: (node.innerText || node.getAttribute('aria-label') || node.getAttribute('title') || '').trim().slice(0, 80),
                href: node.getAttribute('href') || ''
              };
            });
        }
        """
    )


def _overflow_count(page) -> int:
    return int(
        page.evaluate(
            """
            () => {
              const width = document.documentElement.clientWidth;
              const isClippedByAncestor = (node) => {
                let current = node.parentElement;
                while (current) {
                  const style = window.getComputedStyle(current);
                  const clipsX = ['hidden', 'clip'].includes(style.overflowX) || ['hidden', 'clip'].includes(style.overflow);
                  if (clipsX) {
                    const currentRect = current.getBoundingClientRect();
                    const rect = node.getBoundingClientRect();
                    const clippedWithinAncestor =
                      rect.right <= currentRect.right + 1 &&
                      rect.left >= currentRect.left - 1;
                    if (!clippedWithinAncestor) {
                      return true;
                    }
                  }
                  current = current.parentElement;
                }
                return false;
              };
              return Array.from(document.querySelectorAll('body *')).filter((node) => {
                const rect = node.getBoundingClientRect();
                if (!(rect.width > 0 && rect.right > width + 1)) {
                  return false;
                }
                return !isClippedByAncestor(node);
              }).length;
            }
            """
        )
    )


def verify_project(project_name: str, *, port: int, click_limit: int, timeout_seconds: int) -> dict[str, object]:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Playwright is required. Install with `.venv/bin/python -m pip install playwright` "
            "and `.venv/bin/python -m playwright install chromium`."
        ) from exc

    normalized_name = normalize_project_directory_name(project_name)
    project_dir = PROJECTS_ROOT / normalized_name
    if not project_dir.exists():
        raise RuntimeError(f"Project not found: {project_dir}")
    if not (project_dir / "package.json").exists():
        raise RuntimeError(f"Web app project must contain package.json: {project_dir}")

    artifact_dir = project_dir / "product" / "browser-verification"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    url = f"http://127.0.0.1:{port}"
    server = _start_dev_server(project_dir, port)
    console_errors: list[dict[str, str]] = []
    page_errors: list[str] = []
    viewport_results: list[dict[str, object]] = []
    click_results: list[dict[str, str]] = []

    try:
        _wait_for_server(url, timeout_seconds)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for name, width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.on(
                    "console",
                    lambda message: console_errors.append(_console_entry(message))
                    if message.type in {"error", "warning"}
                    else None,
                )
                page.on("pageerror", lambda exc: page_errors.append(str(exc)))
                page.goto(url, wait_until="networkidle", timeout=timeout_seconds * 1000)
                screenshot_path = artifact_dir / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                overflow_count = _overflow_count(page)
                targets = _visible_targets(page)
                viewport_results.append(
                    {
                        "name": name,
                        "width": width,
                        "height": height,
                        "title": page.title(),
                        "url": page.url,
                        "screenshot": str(screenshot_path.relative_to(REPO_ROOT)),
                        "horizontal_overflow_count": overflow_count,
                        "visible_interaction_targets": len(targets),
                    }
                )
                page.close()

            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(url, wait_until="networkidle", timeout=timeout_seconds * 1000)
            for target in _visible_targets(page)[:click_limit]:
                locator = page.locator(f'[data-ai-builder-verify-id="{target["verify_id"]}"]')
                try:
                    locator.click(timeout=3_000)
                    page.wait_for_load_state("networkidle", timeout=5_000)
                    click_results.append({"target": target.get("text") or target.get("tag", ""), "status": "PASS"})
                except PlaywrightError as exc:
                    click_results.append(
                        {"target": target.get("text") or target.get("tag", ""), "status": "FAIL", "detail": str(exc)}
                    )
            page.close()
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:  # pragma: no cover - timing dependent
            server.kill()

    blocking_failures = []
    if page_errors:
        blocking_failures.append("page errors were raised")
    if any(entry["type"] == "error" for entry in console_errors):
        blocking_failures.append("console errors were raised")
    overflow_failures = [
        result["name"]
        for result in viewport_results
        if int(result.get("horizontal_overflow_count", 0)) > 0
    ]
    if overflow_failures:
        blocking_failures.append("horizontal overflow was detected in " + ", ".join(overflow_failures))
    failed_clicks = [result for result in click_results if result.get("status") == "FAIL"]
    if failed_clicks:
        blocking_failures.append("interaction click checks failed")

    status = "PASS" if not blocking_failures else "FAIL"
    result = {
        "status": status,
        "project_name": normalized_name,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "viewports": viewport_results,
        "clicks": click_results,
        "console_findings": console_errors[:20],
        "page_errors": page_errors[:20],
        "blocking_failures": blocking_failures,
    }
    evidence_path = project_dir / "product" / "browser-verification.json"
    evidence_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Playwright browser verification for an AI Builder OS web app.")
    parser.add_argument("project_name", help="Project slug under projects/")
    parser.add_argument("--port", type=int, default=8877, help="Local dev-server port.")
    parser.add_argument("--click-limit", type=int, default=5, help="Maximum visible buttons/links to click.")
    parser.add_argument("--timeout-seconds", type=int, default=45, help="Server and page timeout.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = verify_project(
        args.project_name,
        port=args.port,
        click_limit=args.click_limit,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
