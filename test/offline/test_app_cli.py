"""Offline CLI tests.

Verifies: FR-007.
"""

from pathlib import Path

import pytest

from pennyguard.app import main


def test_subcommands_run(tmp_path: Path):
    # verifies: FR-007 — add/list/status/eval execute without raising.
    data = tmp_path / "data"
    assert main(["add", "--description", "Coffee", "--amount", "10.00", "--date", "2026-11-01"], data_dir=data) == 0
    assert main(["list"], data_dir=data) == 0
    assert main(["status"], data_dir=data) == 0
    assert main(["eval"], data_dir=data) == 0


def test_unknown_command_returns_error(tmp_path: Path):
    # negative test: unknown command exits with a documented non-zero code (SystemExit 2).
    with pytest.raises(SystemExit) as exc:
        main(["bogus"], data_dir=tmp_path / "data")
    assert exc.value.code == 2
