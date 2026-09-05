"""Regression for Aider-AI/aider#5620, second entry route (/read-only + /add).

An image outside the repo is allowed as read-only from anywhere. Promoting it
with /add reaches GitRepo.path_in_repo() with an out-of-root absolute path,
which must answer "not tracked" rather than raise ValueError.
"""

import os
import tempfile
from pathlib import Path
from unittest import TestCase

from aider.coders import Coder
from aider.commands import Commands
from aider.io import InputOutput
from aider.models import Model
from aider.utils import GitTemporaryDirectory


class TestIssue5620AddRoute(TestCase):
    def test_add_promotes_outside_readonly_image_without_crash(self):
        with tempfile.TemporaryDirectory() as outside_dir:
            outside_image = Path(outside_dir) / "outside.png"
            outside_image.write_bytes(b"not really a png")
            with GitTemporaryDirectory():
                io = InputOutput(pretty=False, fancy_input=False, yes=True)
                coder = Coder.create(Model("gpt-4o"), None, io)
                commands = Commands(io, coder)

                commands.cmd_read_only(str(outside_image))
                self.assertEqual(len(coder.abs_read_only_fnames), 1)

                # Must not raise; the file is not part of the repository.
                commands.cmd_add(str(outside_image))

                self.assertEqual(len(coder.abs_fnames), 0)
                self.assertTrue(
                    any(
                        os.path.samefile(str(outside_image), fname)
                        for fname in coder.abs_read_only_fnames
                    )
                )
