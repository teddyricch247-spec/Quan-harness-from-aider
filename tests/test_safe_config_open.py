from pathlib import Path
from unittest import mock

from aider.args import _safe_open_config_file, get_parser


def test_safe_open_config_file_readable(tmp_path):
    conf = tmp_path / ".aider.conf.yml"
    conf.write_text("model: gpt-4o\n", encoding="utf-8")
    with _safe_open_config_file(str(conf)) as f:
        assert "gpt-4o" in f.read()


def test_safe_open_config_file_permission_denied(tmp_path):
    conf = tmp_path / ".aider.conf.yml"
    conf.write_text("model: gpt-4o\n", encoding="utf-8")
    real_open = open

    def boom(path, *args, **kwargs):
        if Path(path) == conf:
            raise PermissionError(13, "Permission denied", str(path))
        return real_open(path, *args, **kwargs)

    with mock.patch("builtins.open", side_effect=boom):
        with _safe_open_config_file(str(conf)) as f:
            # empty YAML mapping so YAMLConfigFileParser accepts it
            assert f.read().strip() in ("{}", "")


def test_get_parser_skips_unreadable_default_config(tmp_path):
    conf = tmp_path / ".aider.conf.yml"
    conf.write_text("model: should-not-load\n", encoding="utf-8")
    real_open = open

    def selective_open(path, *args, **kwargs):
        if Path(path) == conf:
            raise PermissionError(13, "Permission denied", str(path))
        return real_open(path, *args, **kwargs)

    with mock.patch("builtins.open", side_effect=selective_open):
        parser = get_parser([str(conf)], git_root=None)
        args, _ = parser.parse_known_args([])
        # Unreadable conf must not crash; model stays default None
        assert getattr(args, "model", None) is None
