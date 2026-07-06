import os

from aider.utils import safe_abs_path, split_chat_history_markdown


def test_safe_abs_path_symlink_loop(tmp_path):
    # Create circular symlink: a -> b -> a
    link_a = tmp_path / "link_a"
    link_b = tmp_path / "link_b"
    link_a.symlink_to(link_b)
    link_b.symlink_to(link_a)

    # safe_abs_path must not raise, and must return an absolute path
    result = safe_abs_path(str(link_a))
    assert os.path.isabs(result)


def test_split_chat_history_keeps_trailing_tool():
    # A history ending in a tool ("> ") line must not drop that content when
    # include_tool=True. The end-of-loop flush skipped the tool buffer, so a
    # trailing tool message was lost.
    messages = split_chat_history_markdown("> trailing tool output\n", include_tool=True)
    assert messages == [{"role": "tool", "content": "trailing tool output\n"}]
