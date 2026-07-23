import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmark.refactor_tools import find_non_self_methods


class TestRefactorTools(unittest.TestCase):
    def test_find_non_self_methods_skips_invalid_python(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_file = Path(temp_dir) / "invalid.py"
            invalid_file.write_text("class Broken(:\n")

            self.assertEqual(find_non_self_methods(str(invalid_file)), [])

    def test_find_non_self_methods_does_not_reuse_stale_ast(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_file = Path(temp_dir) / "valid.py"
            valid_file.write_text("class Example:\n    def candidate(self):\n        return 1\n")
            invalid_file = Path(temp_dir) / "invalid.py"
            invalid_file.write_text("class Broken(:\n")

            with patch(
                "benchmark.refactor_tools.find_python_files",
                return_value=[str(valid_file), str(invalid_file)],
            ):
                methods = find_non_self_methods(temp_dir)

            self.assertEqual(len(methods), 1)
            self.assertEqual(methods[0][0], str(valid_file))

    def test_find_non_self_methods_propagates_keyboard_interrupt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "source.py"
            source_file.write_text("value = 1\n")

            with patch("benchmark.refactor_tools.ast.parse", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    find_non_self_methods(str(source_file))


if __name__ == "__main__":
    unittest.main()
