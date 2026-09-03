from pathlib import Path
from unittest.mock import patch

from aider.io import InputOutput


def test_input_history_mkdir_failure_does_not_crash(tmp_path):
    """Regression for #5669: mkdir failure must not call tool_warning before console exists."""
    history = tmp_path / "missing-parent" / "history"

    with patch.object(Path, "mkdir", side_effect=OSError("No such file or directory: '.'")):
        io = InputOutput(
            pretty=False,
            fancy_input=False,
            input_history_file=str(history),
            chat_history_file=str(tmp_path / "chat.md"),
        )

    assert io.input_history_file is None
    assert io.console is not None
