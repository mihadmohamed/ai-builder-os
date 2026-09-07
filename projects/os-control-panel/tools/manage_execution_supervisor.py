from __future__ import annotations

import argparse
import os
from pathlib import Path
import plistlib
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
LABEL = "com.openai.ai-builder-os.execution-supervisor"
DEFAULT_DESTINATION = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def launch_agent_payload() -> dict[str, object]:
    runtime_root = Path(os.getenv("AI_BUILDER_OS_RUNTIME_ROOT", REPO_ROOT / "private" / "ai-builder-os" / "runtime"))
    log_dir = runtime_root / "supervisor"
    return {
        "Label": LABEL,
        "ProgramArguments": [
            sys.executable,
            str(PROJECT_ROOT / "tools" / "execution_supervisor.py"),
            "--loop",
            "--interval-seconds",
            "60",
        ],
        "WorkingDirectory": str(REPO_ROOT),
        "EnvironmentVariables": {
            "PYTHONPATH": f"{PROJECT_ROOT / 'src'}:{REPO_ROOT}",
            "AI_BUILDER_OS_RUNTIME_ROOT": str(runtime_root),
        },
        "RunAtLoad": True,
        "KeepAlive": True,
        "ProcessType": "Background",
        "ThrottleInterval": 30,
        "StandardOutPath": "/dev/null",
        "StandardErrorPath": "/dev/null",
    }


def write_plist(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    runtime_root = Path(os.getenv("AI_BUILDER_OS_RUNTIME_ROOT", REPO_ROOT / "private" / "ai-builder-os" / "runtime"))
    log_dir = runtime_root / "supervisor"
    log_dir.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        plistlib.dump(launch_agent_payload(), handle, sort_keys=True)
    try:
        log_dir.chmod(0o700)
        destination.chmod(0o600)
    except OSError:
        pass
    return destination


def _launchctl(*args: str) -> int:
    return subprocess.run(["launchctl", *args], check=False).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the per-user AI Builder OS execution supervisor.")
    parser.add_argument("action", choices=("render", "install", "uninstall", "status"))
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    domain = f"gui/{os.getuid()}"
    service = f"{domain}/{LABEL}"
    if args.action == "render":
        plistlib.dump(launch_agent_payload(), sys.stdout.buffer, sort_keys=True)
        return 0
    if args.action == "status":
        return _launchctl("print", service)
    if args.action == "uninstall":
        return _launchctl("bootout", service)
    destination = write_plist(args.destination.expanduser())
    _launchctl("bootout", service)
    return _launchctl("bootstrap", domain, str(destination))


if __name__ == "__main__":
    raise SystemExit(main())
