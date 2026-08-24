import pytest  # noqa: F401

from aider.run_cmd import run_cmd


def test_run_cmd_echo():
    command = "echo Hello, World!"
    exit_code, output = run_cmd(command)

    assert exit_code == 0
    assert output.strip() == "Hello, World!"

def test_run_cmd_subprocess_reads_in_chunks(mocker):
    mock_process = mocker.MagicMock()
    mock_process.stdout.read.side_effect = ["chunk1", "chunk2", ""]
    mock_process.wait.return_value = None
    mock_process.returncode = 0
    mocker.patch("aider.run_cmd.subprocess.Popen", return_value=mock_process)

    from aider.run_cmd import run_cmd_subprocess

    code, out = run_cmd_subprocess("echo test")
    assert code == 0
    assert out == "chunk1chunk2"
    mock_process.stdout.read.assert_called_with(4096)
