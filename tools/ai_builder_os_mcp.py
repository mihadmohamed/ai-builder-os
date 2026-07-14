#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"
sys.path.insert(0, str(SOURCE_ROOT))
sys.path.insert(0, str(REPO_ROOT))

from codex_bridge.server import main  # noqa: E402


if __name__ == "__main__":
    main()
