import os

import pytest

from aider.utils import format_tokens, safe_abs_path


def test_safe_abs_path_symlink_loop(tmp_path):
    # Create circular symlink: a -> b -> a
    link_a = tmp_path / "link_a"
    link_b = tmp_path / "link_b"
    link_a.symlink_to(link_b)
    link_b.symlink_to(link_a)

    # safe_abs_path must not raise, and must return an absolute path
    result = safe_abs_path(str(link_a))
    assert os.path.isabs(result)


@pytest.mark.parametrize(
    "count,expected",
    [
        (0, "0"),
        (999, "999"),
        (1000, "1.0k"),
        (9999, "10.0k"),
        (10000, "10k"),
        (10499, "10k"),
        # Halfway values must round up, not to the nearest even thousand
        (10500, "11k"),
        (11500, "12k"),
        (12500, "13k"),
        (12501, "13k"),
    ],
)
def test_format_tokens(count, expected):
    assert format_tokens(count) == expected
