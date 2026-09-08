"""
Tests for Story 1.3: Domain ports and dependency direction.

Acceptance criteria (from epics.md):
  AC1 - Adapters depend on core; core depends on nothing.
  AC2 - A fake adapter can satisfy each port for tests.

This test asserts the dependency direction structurally by inspecting imports.
Core modules must not import from adapters, app, or edge.
"""

import ast
import importlib
import inspect
import sys
from pathlib import Path

import pytest

# Resolve the src root so we can locate modules by path
SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "recollect"
CORE_ROOT = SRC_ROOT / "core"

FORBIDDEN_IMPORTS_IN_CORE = {"recollect.adapters", "recollect.app", "recollect.edge", "recollect.web"}


def _collect_python_files(directory: Path) -> list[Path]:
    return list(directory.rglob("*.py"))


def _get_imports(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


# ---------------------------------------------------------------------------
# AC1: core depends on nothing outside itself
# ---------------------------------------------------------------------------

def test_core_does_not_import_adapters_or_app_or_edge() -> None:
    violations: list[str] = []
    for py_file in _collect_python_files(CORE_ROOT):
        for imp in _get_imports(py_file):
            for forbidden in FORBIDDEN_IMPORTS_IN_CORE:
                if imp.startswith(forbidden):
                    violations.append(f"{py_file.relative_to(SRC_ROOT)}: imports {imp}")

    assert not violations, (
        "core/ must not import from adapters/, app/, edge/, or web/. Violations:\n"
        + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# AC2: fake adapter satisfies every port
# ---------------------------------------------------------------------------

def test_fake_log_satisfies_observation_log_port() -> None:
    from recollect.adapters.fake_log import FakeObservationLog
    from recollect.core.ports.log_port import ObservationLogPort

    assert issubclass(FakeObservationLog, ObservationLogPort), (
        "FakeObservationLog must implement ObservationLogPort (Story 1.3 AC2)"
    )


def test_system_clock_satisfies_clock_port() -> None:
    from recollect.core.ports.clock_port import ClockPort, SystemClock

    assert issubclass(SystemClock, ClockPort)


def test_all_abstract_methods_implemented_on_fake_log() -> None:
    from recollect.adapters.fake_log import FakeObservationLog
    from recollect.core.ports.log_port import ObservationLogPort
    import inspect

    abstract_methods = {
        name
        for name, _ in inspect.getmembers(ObservationLogPort, predicate=inspect.isfunction)
        if getattr(getattr(ObservationLogPort, name), "__isabstractmethod__", False)
    }
    fake_methods = {
        name
        for name, _ in inspect.getmembers(FakeObservationLog, predicate=inspect.isfunction)
    }
    missing = abstract_methods - fake_methods
    assert not missing, f"FakeObservationLog is missing implementations: {missing}"
