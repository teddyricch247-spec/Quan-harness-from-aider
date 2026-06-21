import unittest
from pathlib import Path

from aider.coders import Coder
from aider.dump import dump  # noqa: F401
from aider.io import InputOutput
from aider.models import Model
from aider.utils import GitTemporaryDirectory


class TestPatchCoderSecurity(unittest.TestCase):
    """Path-confinement tests for the patch coder.

    The patch coder takes file paths -- including ``*** Move to:`` targets --
    straight from the LLM response. These tests pin that such paths cannot
    escape the repository root, while a legitimate in-repo move still works.
    """

    def setUp(self):
        """Set up a cheap model handle shared by the tests."""
        self.GPT35 = Model("gpt-3.5-turbo")

    def test_rejects_move_outside_repo(self):
        """A ``*** Move to:`` path that escapes the repo must be refused.

        The move target never passes the in-chat edit confirmation, so an
        out-of-root target must be rejected outright rather than silently
        overwriting a file outside the project and deleting the source.
        """
        with GitTemporaryDirectory() as repo_dir:
            src = Path(repo_dir) / "sample.txt"
            src.write_text("Original content\n")

            outside = Path(repo_dir).parent / "escape_victim.txt"
            outside.write_text("PRECIOUS\n")
            self.addCleanup(lambda: outside.exists() and outside.unlink())

            # yes=False: refuse every confirmation. The source file is added to
            # the chat, so the source edit needs no confirmation -- only the
            # missing move-target guard stands between the LLM and the write.
            io = InputOutput(yes=False)
            coder = Coder.create(self.GPT35, "patch", io=io, fnames=[str(src)])

            coder.partial_response_content = (
                "*** Begin Patch\n"
                "*** Update File: sample.txt\n"
                "*** Move to: ../escape_victim.txt\n"
                "@@\n"
                "-Original content\n"
                "+Hacked content\n"
                "*** End Patch\n"
            )

            coder.apply_updates()

            # The out-of-repo file is untouched and the source still exists.
            self.assertEqual(outside.read_text(), "PRECIOUS\n")
            self.assertTrue(src.exists())
            self.assertEqual(src.read_text(), "Original content\n")

    def test_apply_edits_rejects_add_outside_repo(self):
        """``apply_edits`` refuses an ADD whose path escapes the repo.

        Driven at the ``apply_edits`` level with a constructed action so the
        ``action.path`` guard is exercised directly, independent of the
        separate new-file confirmation in ``allowed_to_edit``.
        """
        from aider.coders.patch_coder import ActionType, PatchAction

        with GitTemporaryDirectory() as repo_dir:
            outside = Path(repo_dir).parent / "escape_added.txt"
            self.addCleanup(lambda: outside.exists() and outside.unlink())

            io = InputOutput(yes=True)
            coder = Coder.create(self.GPT35, "patch", io=io)

            action = PatchAction(
                type=ActionType.ADD,
                path="../escape_added.txt",
                new_content="pwned\n",
            )
            with self.assertRaises(ValueError):
                coder.apply_edits([("../escape_added.txt", action)])

            self.assertFalse(outside.exists())

    def test_allows_move_within_repo(self):
        """A legitimate in-repo move still applies (no false positive)."""
        with GitTemporaryDirectory() as repo_dir:
            src = Path(repo_dir) / "sample.txt"
            src.write_text("Original content\n")

            io = InputOutput(yes=True)
            coder = Coder.create(self.GPT35, "patch", io=io, fnames=[str(src)])

            coder.partial_response_content = (
                "*** Begin Patch\n"
                "*** Update File: sample.txt\n"
                "*** Move to: renamed.txt\n"
                "@@\n"
                "-Original content\n"
                "+Updated content\n"
                "*** End Patch\n"
            )

            coder.apply_updates()

            moved = Path(repo_dir) / "renamed.txt"
            self.assertTrue(moved.exists())
            self.assertEqual(moved.read_text(), "Updated content\n")
            self.assertFalse(src.exists())


if __name__ == "__main__":
    unittest.main()
