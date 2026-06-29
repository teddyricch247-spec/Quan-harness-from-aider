import sys
from typing import Any, Dict

import pytest  # noqa: F401

import aider.run_cmd as run_cmd_module
from aider.run_cmd import run_cmd, run_cmd_pexpect, run_cmd_subprocess


def test_run_cmd_echo():
    command = "echo Hello, World!"
    exit_code, output = run_cmd(command)

    assert exit_code == 0
    assert output.strip() == "Hello, World!"


def test_run_cmd_subprocess_preserves_requested_cwd(tmp_path):
    requested_cwd = tmp_path / "requested"
    requested_cwd.mkdir()

    command = f'"{sys.executable}" -c "import os; print(os.getcwd())"'
    exit_code, output = run_cmd_subprocess(command, cwd=str(requested_cwd))

    assert exit_code == 0
    assert output.strip() == str(requested_cwd)


def _patch_pexpect_spawn(monkeypatch, spawn_impl, shell_exists=True):
    captured: Dict[str, Any] = {}

    def fake_spawn(shell, args, encoding, cwd=None):
        captured["shell"] = shell
        captured["args"] = args
        captured["encoding"] = encoding
        captured["cwd"] = cwd
        return spawn_impl(args, cwd)

    monkeypatch.setattr(run_cmd_module.pexpect, "spawn", fake_spawn, raising=False)
    monkeypatch.setattr(run_cmd_module.os.path, "exists", lambda _: shell_exists)

    return captured


def test_run_cmd_pexpect_preserves_interact_output_capture(monkeypatch):
    expected_output = "interactive output"

    class FakeChild:
        exitstatus = 0

        def interact(self, output_filter):
            output_filter(expected_output.encode())

        def close(self):
            pass

    captured = _patch_pexpect_spawn(
        monkeypatch,
        lambda args, cwd: FakeChild(),
    )

    exit_code, output = run_cmd_pexpect("printf 'interactive output'")

    assert exit_code == 0
    assert output == expected_output
    assert captured["args"] == ["-c", "printf 'interactive output'"]


def test_run_cmd_pexpect_preserves_requested_cwd_when_interactive_startup_would_cd(
    tmp_path, monkeypatch
):
    requested_cwd = tmp_path / "requested"
    requested_cwd.mkdir()
    startup_cwd = tmp_path / "startup"
    startup_cwd.mkdir()

    captured: Dict[str, Any] = {}

    class FakeChild:
        exitstatus = 0

        def __init__(self, args, cwd):
            captured["args"] = args
            captured["cwd"] = cwd

        def interact(self, output_filter):
            if "-i" in captured["args"]:
                output_filter(f"{startup_cwd}\n".encode())
            else:
                output_filter(f"{captured['cwd']}\n".encode())

        def close(self):
            pass

    _patch_pexpect_spawn(monkeypatch, FakeChild)

    exit_code, output = run_cmd_pexpect("pwd", cwd=str(requested_cwd))

    assert exit_code == 0
    assert captured["args"] == ["-c", "pwd"]
    assert output.strip() == str(requested_cwd)
