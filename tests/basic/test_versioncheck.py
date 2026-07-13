from unittest import TestCase
from unittest.mock import patch

from aider.io import InputOutput
from aider.versioncheck import check_version


class TestVersionCheck(TestCase):
    def test_check_version_survives_permission_error_on_cache_dir(self):
        io = InputOutput(pretty=False, fancy_input=False, yes=False)

        with (
            patch(
                "requests.get",
                side_effect=Exception("network error"),
            ),
            patch(
                "pathlib.Path.mkdir",
                side_effect=PermissionError("[Errno 13] Permission denied: '/.aider'"),
            ),
        ):
            # Should not raise — PermissionError in the finally block must be swallowed
            result = check_version(io)

        self.assertFalse(result)
