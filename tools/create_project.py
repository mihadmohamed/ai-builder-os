from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

from common import (
    REPO_ROOT,
    PROJECTS_ROOT,
    REQUIRED_PROJECT_PATHS,
    TEMPLATE_ROOT,
    normalize_project_directory_name,
    project_display_name,
    should_treat_as_text,
)


WEB_APP_PACKAGE_JSON = """{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "@next/font": "latest",
    "next": "latest",
    "react": "latest",
    "react-dom": "latest"
  },
  "devDependencies": {
    "@types/node": "latest",
    "@types/react": "latest",
    "@types/react-dom": "latest",
    "typescript": "^5.9.2"
  }
}
"""


WEB_APP_PAGE = """export default function Home() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "48px", maxWidth: "920px" }}>
      <p style={{ color: "#64748b", marginBottom: "12px" }}>AI Builder OS web app project</p>
      <h1 style={{ fontSize: "40px", lineHeight: 1.1, margin: 0 }}>[Project Name]</h1>
      <p style={{ color: "#334155", fontSize: "18px", lineHeight: 1.6 }}>
        Replace this starter surface with the first approved product workflow.
      </p>
    </main>
  );
}
"""


WEB_APP_LAYOUT = """export const metadata = {
  title: "[Project Name]",
  description: "AI Builder OS web app project",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
"""


def replace_placeholders(path: Path, name: str, display_name: str) -> None:
    if not should_treat_as_text(path) or path.name == ".gitkeep":
        return

    content = path.read_text()
    updated = (
        content.replace("[INSERT PROJECT]", name)
        .replace("[project name]", name)
        .replace("[Project Name]", display_name)
    )
    path.write_text(updated)


def initialize_project_files(
    destination: Path,
    project_name: str,
    display_name: str,
    product_title: str | None,
    initial_requirement_title: str | None,
    initial_requirement: str | None,
    ui_runtime: str | None,
) -> None:
    readme_path = destination / "README.md"
    requirements_path = destination / "product" / "requirements.md"
    tasks_path = destination / "product" / "tasks.md"
    ui_runtime_path = destination / "product" / "ui-runtime.json"

    if product_title:
        readme_path.write_text(readme_path.read_text().replace("# Project Template", f"# {product_title}"))
        requirements_path.write_text(
            requirements_path.read_text().replace(f"# Product: {display_name}", f"# Product: {product_title}")
        )
        tasks_path.write_text(
            tasks_path.read_text().replace(f"# Tasks — {display_name}", f"# Tasks — {product_title}")
        )

    if initial_requirement:
        requirements_path.write_text(
            requirements_path.read_text().replace(
                "### R1 — Initial requirement",
                f"### R1 — {(initial_requirement_title or 'Initial requirement').strip()}",
            ).replace(
                "Replace this with the first real requirement.",
                initial_requirement.strip(),
            )
        )

    normalized_runtime = (ui_runtime or "streamlit").strip() or "streamlit"
    ui_runtime_path.write_text(
        '{\n  "default_ui_runtime": "%s",\n  "design": {\n'
        '    "mode": "code_first",\n    "figma_file_url": "",\n'
        '    "figma_file_name": "",\n    "figma_references": []\n  }\n}\n' % normalized_runtime
    )

    if normalized_runtime == "web_app":
        (destination / "package.json").write_text(WEB_APP_PACKAGE_JSON)
        app_dir = destination / "app"
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "page.tsx").write_text(WEB_APP_PAGE.replace("[Project Name]", display_name))
        (app_dir / "layout.tsx").write_text(WEB_APP_LAYOUT.replace("[Project Name]", display_name))


def _is_runtime_only_existing_project_dir(destination: Path) -> bool:
    if not destination.exists() or not destination.is_dir():
        return False
    top_level_names = {child.name for child in destination.iterdir()}
    if not top_level_names:
        return False
    if not top_level_names.issubset({"data", "users"}):
        return False
    return not any((destination / relative_path).exists() for relative_path in REQUIRED_PROJECT_PATHS)


def _scaffold_into_existing_runtime_only_dir(
    destination: Path,
    normalized_project_name: str,
    display_name: str,
    product_title: str | None,
    initial_requirement_title: str | None,
    initial_requirement: str | None,
    ui_runtime: str | None,
) -> Path:
    with tempfile.TemporaryDirectory(prefix="project-scaffold-") as temp_dir:
        preserved_root = Path(temp_dir) / "preserved"
        preserved_root.mkdir(parents=True, exist_ok=True)
        for child in list(destination.iterdir()):
            shutil.move(str(child), preserved_root / child.name)
        destination.rmdir()
        shutil.copytree(TEMPLATE_ROOT, destination)
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                replace_placeholders(path, normalized_project_name, display_name)
        initialize_project_files(
            destination,
            normalized_project_name,
            display_name,
            product_title=product_title,
            initial_requirement_title=initial_requirement_title,
            initial_requirement=initial_requirement,
            ui_runtime=ui_runtime,
        )
        for child in preserved_root.iterdir():
            shutil.move(str(child), destination / child.name)
    return destination


def scaffold_project(
    project_name: str,
    force: bool = False,
    display_name: str | None = None,
    product_title: str | None = None,
    initial_requirement_title: str | None = None,
    initial_requirement: str | None = None,
    ui_runtime: str | None = None,
) -> Path:
    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"Template root not found: {TEMPLATE_ROOT}")

    normalized_project_name = normalize_project_directory_name(project_name)
    destination = PROJECTS_ROOT / normalized_project_name
    if destination.exists():
        if _is_runtime_only_existing_project_dir(destination):
            display_name = display_name or project_display_name(normalized_project_name)
            return _scaffold_into_existing_runtime_only_dir(
                destination,
                normalized_project_name,
                display_name,
                product_title=product_title,
                initial_requirement_title=initial_requirement_title,
                initial_requirement=initial_requirement,
                ui_runtime=ui_runtime,
            )
        if not force:
            raise FileExistsError(
                f"Project already exists: {destination}. Use --force to replace it."
            )
        shutil.rmtree(destination)

    shutil.copytree(TEMPLATE_ROOT, destination)

    display_name = display_name or project_display_name(normalized_project_name)
    for path in sorted(destination.rglob("*")):
        if path.is_file():
            replace_placeholders(path, normalized_project_name, display_name)

    initialize_project_files(
        destination,
        normalized_project_name,
        display_name,
        product_title=product_title,
        initial_requirement_title=initial_requirement_title,
        initial_requirement=initial_requirement,
        ui_runtime=ui_runtime,
    )

    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a new AI Builder OS project from the shared template."
    )
    parser.add_argument("project_name", help="Project directory slug, e.g. parentmate or my-new-project")
    parser.add_argument(
        "--display-name",
        help="Optional human-readable project name used in placeholders.",
    )
    parser.add_argument(
        "--product-title",
        help="Optional product title for README and product docs.",
    )
    parser.add_argument(
        "--initial-requirement-title",
        help="Optional first requirement title to seed into product/requirements.md.",
    )
    parser.add_argument(
        "--initial-requirement",
        help="Optional first requirement description to seed into product/requirements.md.",
    )
    parser.add_argument(
        "--ui-runtime",
        choices=("streamlit", "web_app"),
        default="streamlit",
        help="Default UI runtime for the project.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the destination project directory if it already exists.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    destination = scaffold_project(
        args.project_name,
        force=args.force,
        display_name=args.display_name,
        product_title=args.product_title,
        initial_requirement_title=args.initial_requirement_title,
        initial_requirement=args.initial_requirement,
        ui_runtime=args.ui_runtime,
    )
    print(f"Created project: {destination.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
