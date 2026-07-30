"""Command-line entry point for unused-imports-cli."""
from __future__ import annotations

import argparse
import os
import sys

from .core import find_unused_imports

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".tox", "build", "dist", ".eggs"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unused-imports-cli",
        description="Scan Python files for imports that are never used.",
    )
    parser.add_argument(
        "paths", nargs="+", help="One or more .py files or directories to scan (directories are searched recursively)"
    )
    return parser


def _iter_python_files(paths: list[str]) -> list[str]:
    files: list[str] = []
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in sorted(names):
                    if name.endswith(".py"):
                        files.append(os.path.join(root, name))
        else:
            files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    files = _iter_python_files(args.paths)

    had_error = False
    had_unused = False

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                source = fh.read()
        except OSError as exc:
            print(f"unused-imports-cli: error: {path}: {exc}", file=sys.stderr)
            had_error = True
            continue

        try:
            unused = find_unused_imports(source, filename=path)
        except SyntaxError as exc:
            print(f"unused-imports-cli: error: {path}: {exc.msg} (line {exc.lineno})", file=sys.stderr)
            had_error = True
            continue

        for item in unused:
            had_unused = True
            print(f"{path}:{item.line}: unused import '{item.name}'")

    if had_error:
        return 2
    return 1 if had_unused else 0


if __name__ == "__main__":
    raise SystemExit(main())
