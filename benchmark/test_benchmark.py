# flake8: noqa: E501

import unittest
from pathlib import Path

from benchmark import cleanup_test_output


class TestCleanupTestOutput(unittest.TestCase):
    def setUp(self):
        self.testdir = Path("tmp.benchmarks/2024-01-01/python/exercises/practice/two-fer")

    def test_removes_timing_info(self):
        output = "Ran 5 tests in 0.003s\nOK"
        expected = "Ran 5 tests \nOK"
        self.assertEqual(cleanup_test_output(output, self.testdir), expected)

    def test_output_without_timing_is_unchanged(self):
        output = "OK"
        self.assertEqual(cleanup_test_output(output, self.testdir), "OK")

    def test_replaces_testdir_path_with_its_name(self):
        output = f"FAILED {self.testdir}/two_fer.py::test_name - AssertionError"
        expected = "FAILED two-fer/two_fer.py::test_name - AssertionError"
        self.assertEqual(cleanup_test_output(output, self.testdir), expected)

    def test_removes_timing_and_path_together(self):
        output = f"1 failed in 2.50s\n{self.testdir}/two_fer.py"
        expected = "1 failed \ntwo-fer/two_fer.py"
        self.assertEqual(cleanup_test_output(output, self.testdir), expected)


if __name__ == "__main__":
    unittest.main()
