"""Core logic for detecting unused imports via the ast module."""
from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass
class ImportBinding:
    """A single name bound into scope by an import statement."""

    binding: str  # the identifier accessible in code, e.g. "os" or "d"
    display: str  # human-readable form, e.g. "os.path" or "a.b.c as d"
    line: int


@dataclass
class UnusedImport:
    line: int
    name: str


def _collect_imports(tree: ast.AST) -> list[ImportBinding]:
    bindings: list[ImportBinding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    bindings.append(
                        ImportBinding(
                            binding=alias.asname,
                            display=f"{alias.name} as {alias.asname}",
                            line=node.lineno,
                        )
                    )
                else:
                    bindings.append(
                        ImportBinding(
                            binding=alias.name.split(".")[0],
                            display=alias.name,
                            line=node.lineno,
                        )
                    )
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            for alias in node.names:
                if alias.name == "*":
                    # Star imports make it impossible to know what's used;
                    # skip rather than guess.
                    continue
                if not prefix:
                    full = alias.name
                elif prefix.endswith("."):
                    full = f"{prefix}{alias.name}"
                else:
                    full = f"{prefix}.{alias.name}"
                if alias.asname:
                    bindings.append(
                        ImportBinding(
                            binding=alias.asname,
                            display=f"{full} as {alias.asname}",
                            line=node.lineno,
                        )
                    )
                else:
                    bindings.append(
                        ImportBinding(binding=alias.name, display=full, line=node.lineno)
                    )
    return bindings


def _collect_used_names(tree: ast.AST) -> set[str]:
    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            continue
        if isinstance(node, ast.ImportFrom):
            continue
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            # Attribute access nests a Name/Attribute in .value, which
            # ast.walk visits separately, so no extra work is needed here.
            continue

    # Names re-exported via a static `__all__ = [...]` / (...) list count
    # as used, even though they're never referenced as a bare Name.
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                value = node.value
                if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                    for elt in value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            used.add(elt.value)
    return used


def find_unused_imports(source: str, filename: str = "<string>") -> list[UnusedImport]:
    """Parse `source` and return imports that are never referenced.

    Detection is file-scoped: an import used anywhere in the file (not
    just within its enclosing function/class) counts as used. Names
    referenced only inside string type annotations are not detected as
    uses, which is a known limitation.
    """
    tree = ast.parse(source, filename=filename)
    imports = _collect_imports(tree)
    used = _collect_used_names(tree)

    unused: list[UnusedImport] = []
    for imp in imports:
        if imp.binding not in used:
            unused.append(UnusedImport(line=imp.line, name=imp.display))
    unused.sort(key=lambda u: u.line)
    return unused
