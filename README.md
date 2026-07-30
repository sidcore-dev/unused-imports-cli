# unused-imports-cli

A small, dependency-free command-line tool that scans Python files with
the `ast` module and reports imports that are bound but never referenced
anywhere else in the file.

## Why

Unused imports pile up quietly as code evolves — a refactor removes the
last use of something and the `import` line gets left behind. They're
harmless but noisy, and most full linters are heavyweight to reach for
just to catch this one thing. `unused-imports-cli` does one job: point
it at files or directories and it tells you exactly which imports aren't
pulling their weight.

## Install

```bash
pip install .
```

This installs an `unused-imports-cli` command on your PATH.

## Usage

```bash
unused-imports-cli src/
```

Example output:

```
src/app/utils.py:3: unused import 'json'
src/app/utils.py:7: unused import 'os.path as osp'
src/app/models.py:1: unused import 'typing.Optional'
```

Accepts any mix of individual files and directories; directories are
searched recursively for `.py` files (skipping `.git`, `__pycache__`,
`.venv`, `venv`, `.tox`, `build`, `dist`, and `.eggs`).

```bash
unused-imports-cli app.py lib/ tests/test_app.py
```

### How detection works

- Handles `import x`, `import x as y`, `from x import y`, and
  `from x import y as z` (including relative imports like
  `from . import y`).
- An import counts as "used" if its bound name appears anywhere else in
  the file — including inside functions, classes, decorators, and type
  annotations — or if it's re-exported through a static
  `__all__ = [...]` list.
- Detection is file-scoped, not function-scoped: an import used
  somewhere else in the file won't be flagged even if it's unrelated to
  where it was imported.
- `from x import *` is skipped rather than guessed at, since there's no
  way to know what names it introduces.
- Names referenced only inside string type hints (e.g. `-> "Foo"`) are
  not detected as uses — this is a known limitation.

### Exit codes

- `0` — no unused imports found
- `1` — one or more unused imports found
- `2` — a file couldn't be read or failed to parse

```bash
unused-imports-cli src/ || echo "found unused imports!"
```

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
