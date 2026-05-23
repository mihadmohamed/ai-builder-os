from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import (
    REPO_ROOT,
    PROJECTS_ROOT,
    TEMPLATE_ROOT,
    normalize_project_directory_name,
    project_display_name,
    should_treat_as_text,
)


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
) -> None:
    readme_path = destination / "README.md"
    requirements_path = destination / "product" / "requirements.md"
    tasks_path = destination / "product" / "tasks.md"

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


def scaffold_project(
    project_name: str,
    force: bool = False,
    display_name: str | None = None,
    product_title: str | None = None,
    initial_requirement_title: str | None = None,
    initial_requirement: str | None = None,
) -> Path:
    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"Template root not found: {TEMPLATE_ROOT}")

    normalized_project_name = normalize_project_directory_name(project_name)
    destination = PROJECTS_ROOT / normalized_project_name
    if destination.exists():
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
    )
    print(f"Created project: {destination.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
