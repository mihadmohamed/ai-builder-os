#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import sys


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = PLUGIN_ROOT.parents[1]
CORE_SERVER = CORE_ROOT / "tools" / "ai_builder_os_mcp.py"
CORE_PYTHON = CORE_ROOT / ".venv" / "bin" / "python"


def main() -> None:
    if not CORE_SERVER.is_file():
        raise SystemExit(f"AI Builder OS core server is missing: {CORE_SERVER}")
    python = CORE_PYTHON if CORE_PYTHON.is_file() else Path(sys.executable)
    os.execv(str(python), [str(python), str(CORE_SERVER)])


if __name__ == "__main__":
    main()
