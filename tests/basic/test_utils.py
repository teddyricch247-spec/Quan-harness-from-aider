import base64
import os

from aider.io import InputOutput
from aider.utils import is_image_file, safe_abs_path


def test_is_image_file_ignores_extension_case():
    assert is_image_file("photo.png")
    assert is_image_file("DSC_0001.JPG")
    assert is_image_file("scan.Jpeg")
    assert is_image_file("report.PDF")
    assert not is_image_file("main.py")


def test_read_text_of_uppercase_image_returns_base64(tmp_path):
    data = b"\x89PNG\r\n\x1a\n not really a png"
    fname = tmp_path / "shot.PNG"
    fname.write_bytes(data)

    io = InputOutput(pretty=False, fancy_input=False)
    assert io.read_text(str(fname)) == base64.b64encode(data).decode("utf-8")


def test_safe_abs_path_symlink_loop(tmp_path):
    # Create circular symlink: a -> b -> a
    link_a = tmp_path / "link_a"
    link_b = tmp_path / "link_b"
    link_a.symlink_to(link_b)
    link_b.symlink_to(link_a)

    # safe_abs_path must not raise, and must return an absolute path
    result = safe_abs_path(str(link_a))
    assert os.path.isabs(result)
