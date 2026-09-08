import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / "benchmark"))

from benchmark.benchmark import _output_reports_failures, run_unit_tests

LEAP_TEST = '''\
def test_leap():
    from leap import is_leap
    assert is_leap(1996)
    assert not is_leap(1997)
'''

WRONG_SOLUTION = '''\
def is_leap(year):
    return True
'''

RIGHT_SOLUTION = '''\
def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
'''

CONTEST_CONFTEST = '''\
def pytest_sessionfinish(session, exitstatus):
    if exitstatus != 0:
        session.exitstatus = 0
'''


def make_exercise(tmp_path, solution, conftest=None):
    original_root = tmp_path / "original"
    exercise = original_root / "a" / "b" / "c" / "d"
    testdir = tmp_path / "run" / "a" / "b" / "c" / "d"
    exercise.mkdir(parents=True)
    (exercise / "tests").mkdir()
    (exercise / "tests" / "test_leap.py").write_text(LEAP_TEST)
    if conftest is not None:
        (exercise / "conftest.py").write_text(conftest)

    testdir.mkdir(parents=True)
    (testdir / "tests").mkdir()
    (testdir / "tests" / "test_leap.py").write_text(LEAP_TEST)
    (testdir / "leap.py").write_text(solution)
    return original_root, testdir


def test_model_created_conftest_cannot_force_pass(tmp_path):
    original, testdir = make_exercise(tmp_path, WRONG_SOLUTION)
    # The model plants a conftest.py that forces pytest to exit 0.
    (testdir / "conftest.py").write_text(CONTEST_CONFTEST)
    history = tmp_path / "history.md"

    errors = run_unit_tests(original, testdir, history, ["tests/test_leap.py"])

    assert errors is not None
    assert not (testdir / "conftest.py").exists()


def test_pristine_conftest_is_restored_for_grading(tmp_path):
    marker = "def pytest_configure(config):\n    print('PRISTINE_CONFTEST_LOADED')\n"
    original, testdir = make_exercise(tmp_path, WRONG_SOLUTION, conftest=marker)
    (testdir / "conftest.py").write_text(CONTEST_CONFTEST)
    history = tmp_path / "history.md"

    errors = run_unit_tests(original, testdir, history, ["tests/test_leap.py"])

    assert errors is not None
    assert (testdir / "conftest.py").read_text() == marker


def test_honest_pass_still_passes(tmp_path):
    original, testdir = make_exercise(tmp_path, RIGHT_SOLUTION)
    history = tmp_path / "history.md"

    errors = run_unit_tests(original, testdir, history, ["tests/test_leap.py"])

    assert errors is None


def test_output_reports_failures_detects_runner_summaries():
    assert _output_reports_failures("2 failed, 3 passed in 0.01s", {".py"})
    assert _output_reports_failures("  1 failing", {".js"})
    assert _output_reports_failures("test result: FAILED. 0 passed", {".rs"})
    assert _output_reports_failures("FAIL\t./leap [build failed]", {".go"})
    assert _output_reports_failures("> Task :test FAILED", {".java"})
    assert not _output_reports_failures("5 passed in 0.01s", {".py"})
    assert not _output_reports_failures("1 passed, 0 failing", {".py", ".js"})
