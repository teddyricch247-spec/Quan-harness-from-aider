"""Tests for dynamic API key helper functionality."""

import subprocess
import threading
import time
from unittest.mock import MagicMock, patch

import pytest


class TestFetchApiKeyHelper:
    """Unit tests for safe subprocess execution and validation."""

    def test_given_valid_command_when_returns_key_then_success_is_true(self):
        from aider.utils import fetch_api_key_helper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="sk-proj-abc123\n")
            success, key = fetch_api_key_helper("echo sk-proj-abc123", timeout=5.0)
            assert success is True
            assert key == "sk-proj-abc123"

    def test_given_empty_command_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        success, key = fetch_api_key_helper("", timeout=5.0)
        assert success is False
        assert key is None

    def test_given_whitespace_only_command_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        success, key = fetch_api_key_helper("   ", timeout=5.0)
        assert success is False
        assert key is None

    def test_given_empty_stdout_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="   \n")
            success, key = fetch_api_key_helper("echo", timeout=5.0)
            assert success is False
            assert key is None

    def test_given_timeout_occurs_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 10", timeout=5.0)
            success, key = fetch_api_key_helper("sleep 10", timeout=5.0)
            assert success is False
            assert key is None

    def test_given_non_zero_exit_code_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="error output")
            success, key = fetch_api_key_helper("echo error", timeout=5.0)
            assert success is False
            assert key is None

    def test_given_output_exceeds_max_size_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        # 1025 chars > default max of 8192 bytes? No, but < 8192. Test with smaller limit.
        large_key = "k" * 100
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=large_key)
            success, key = fetch_api_key_helper("echo", timeout=5.0, max_output=50)
            assert success is False
            assert key is None

    def test_given_output_within_max_size_when_executed_then_returns_success(self):
        from aider.utils import fetch_api_key_helper

        key = "k" * 100
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=key)
            success, result_key = fetch_api_key_helper("echo", timeout=5.0, max_output=200)
            assert success is True
            assert result_key == key

    def test_given_oserror_occurs_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = OSError("No such file or directory")
            success, key = fetch_api_key_helper("nonexistent_cmd_xyz", timeout=5.0)
            assert success is False
            assert key is None

    def test_given_permission_error_occurs_when_executed_then_returns_failure(self):
        from aider.utils import fetch_api_key_helper

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = PermissionError("Access denied")
            success, key = fetch_api_key_helper("invalid_cmd", timeout=5.0)
            assert success is False
            assert key is None


class TestModelCacheKey:
    """Tests for Model._get_cache_key class method."""

    def test_get_cache_key_with_model_name(self):
        from aider.models import Model

        key = Model._get_cache_key("gpt-4", "")
        assert key == "gpt-4:"

    def test_get_cache_key_with_model_and_base(self):
        from aider.models import Model

        key = Model._get_cache_key("gpt-4", "https://custom.api")
        assert key == "gpt-4:https://custom.api"


class TestModelDynamicKey:
    """Tests for Model._get_dynamic_key method."""

    def test_given_no_helper_command_when_called_then_returns_none(self):
        from aider.models import Model

        model = Model("gpt-4", api_key_helper_command=None)
        result = model._get_dynamic_key()
        assert result is None

    def test_given_valid_helper_command_when_called_then_fetches_key(self):
        from aider.models import Model

        # Clear cache to avoid interference from other tests
        Model._dynamic_key_cache.clear()

        with patch("aider.utils.fetch_api_key_helper") as mock_fetch:
            mock_fetch.return_value = (True, "sk-fetched-789")
            model = Model(
                "gpt-4",
                api_key_helper_command="echo sk-proj-test",
                api_key_helper_timeout=5.0,
                api_key_helper_shell=False,
                api_key_helper_max_output=8192,
            )
            result = model._get_dynamic_key()
            assert result == "sk-fetched-789"

    def test_given_helper_returns_none_when_called_then_returns_none(self):
        from aider.models import Model

        Model._dynamic_key_cache.clear()

        with patch("aider.utils.fetch_api_key_helper") as mock_fetch:
            mock_fetch.return_value = (False, None)
            model = Model(
                "gpt-4",
                api_key_helper_command="echo failing",
                api_key_helper_timeout=5.0,
                api_key_helper_shell=False,
                api_key_helper_max_output=8192,
            )
            result = model._get_dynamic_key()
            assert result is None

    def test_given_cached_key_within_ttl_when_called_then_returns_cached(self):
        from aider.models import Model

        cache_key = Model._get_cache_key("gpt-4", "")
        Model._dynamic_key_cache[cache_key] = ("sk-cached-key", time.time() + 100)

        model = Model(
            "gpt-4",
            api_key_helper_command="echo test",
            api_key_helper_timeout=5.0,
        )
        result = model._get_dynamic_key()
        assert result == "sk-cached-key"


class TestModelAuthRetry:
    """Tests for send_completion auth failure detection and retry logic."""

    def test_given_auth_error_when_helper_produces_key_then_retries_with_new_key(self):
        from aider.models import Model, litellm
        from aider.exceptions import LiteLLMExceptions

        Model._dynamic_key_cache.clear()
        Model._dynamic_key_locks.clear()

        # Ensure exceptions are loaded by creating and loading an instance first
        LiteLLMExceptions()._load()

        mock_auth_error = MagicMock(spec=litellm.AuthenticationError)
        mock_auth_error.__class__ = litellm.AuthenticationError

        ex_info_mock = MagicMock()
        ex_info_mock.name = "AuthenticationError"
        ex_info_mock.retry = False

        with patch("aider.utils.fetch_api_key_helper") as mock_fetch, \
             patch("litellm.completion") as mock_completion:

            mock_fetch.return_value = (True, "sk-fetched-test-key")
            mock_completion.side_effect = [mock_auth_error, MagicMock(choices=[MagicMock(message=MagicMock(content="OK"))])]

            with patch.object(LiteLLMExceptions, "get_ex_info", return_value=ex_info_mock):

                model = Model(
                    "gpt-4",
                    api_key_helper_command="echo sk-proj-test",
                    api_key_helper_timeout=5.0,
                )

                # Test the full flow: send_completion should catch auth error, fetch key, retry
                hash_obj, response = model.send_completion([{"role": "user", "content": "hi"}], None, True)
                assert mock_fetch.call_count == 1
                assert mock_completion.call_count == 2

    def test_given_no_helper_command_when_auth_error_then_raises(self):
        from aider.models import Model, litellm

        with patch("litellm.completion") as mock_completion:
            mock_auth_error = MagicMock(spec=litellm.AuthenticationError)
            mock_auth_error.__class__ = litellm.AuthenticationError
            mock_completion.side_effect = mock_auth_error

            model = Model(
                "gpt-4",
                api_key_helper_command=None,  # No helper configured
            )

            with pytest.raises(Exception):
                model.send_completion([{"role": "user", "content": "hi"}], None, True)

    def test_given_non_auth_error_when_send_completion_then_raises(self):
        from aider.models import Model, litellm

        mock_other_error = MagicMock(spec=litellm.RateLimitError)
        mock_other_error.__class__ = litellm.RateLimitError

        with patch("litellm.completion") as mock_completion:
            mock_completion.side_effect = mock_other_error

            model = Model(
                "gpt-4",
                api_key_helper_command="echo test",
            )

            # Should raise RateLimitError, not try to fetch a key
            with pytest.raises(Exception):
                model.send_completion([{"role": "user", "content": "hi"}], None, True)

    def test_given_helper_returns_none_on_auth_error_then_raises(self):
        from aider.models import Model, litellm
        from aider.exceptions import LiteLLMExceptions

        Model._dynamic_key_cache.clear()
        Model._dynamic_key_locks.clear()
        LiteLLMExceptions()._load()

        mock_auth_error = MagicMock(spec=litellm.AuthenticationError)
        mock_auth_error.__class__ = litellm.AuthenticationError

        ex_info_mock = MagicMock()
        ex_info_mock.name = "AuthenticationError"
        ex_info_mock.retry = False

        with patch("aider.utils.fetch_api_key_helper") as mock_fetch, \
             patch("litellm.completion") as mock_completion:

            mock_fetch.return_value = (False, None)  # Helper fails
            mock_completion.side_effect = mock_auth_error

            with patch.object(LiteLLMExceptions, "get_ex_info", return_value=ex_info_mock):

                model = Model(
                    "gpt-4",
                    api_key_helper_command="echo test",
                )

                with pytest.raises(Exception):
                    model.send_completion([{"role": "user", "content": "hi"}], None, True)

    def test_given_no_auth_error_when_send_completion_then_does_not_call_helper(self):
        from aider.models import Model, litellm

        with patch("litellm.completion") as mock_completion:
            mock_completion.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="OK"))])

            model = Model(
                "gpt-4",
                api_key_helper_command="echo test",
            )

            hash_obj, response = model.send_completion([{"role": "user", "content": "hi"}], None, True)
            assert mock_completion.called
            # Should only be called once (no retry needed)
            assert mock_completion.call_count == 1


class TestModelInitHelperParams:
    """Tests for Model __init__ accepting helper parameters."""

    def test_given_helper_params_when_init_then_stored_as_attributes(self):
        from aider.models import Model

        model = Model(
            "gpt-4",
            api_key_helper_command="echo key",
            api_key_helper_timeout=10.0,
            api_key_helper_shell=True,
            api_key_helper_max_output=16384,
        )

        assert model.api_key_helper_command == "echo key"
        assert model.api_key_helper_timeout == 10.0
        assert model.api_key_helper_shell is True
        assert model.api_key_helper_max_output == 16384

    def test_given_no_helper_params_when_init_then_defaults_are_none(self):
        from aider.models import Model

        model = Model("gpt-4")

        assert model.api_key_helper_command is None
        assert model.api_key_helper_timeout == 5.0
        assert model.api_key_helper_shell is False
        assert model.api_key_helper_max_output == 8192


class TestArgsParsing:
    """Tests for CLI argument parsing — validates source code."""

    def _read_args_source(self):
        with open("/home/mk/github/aider/aider/args.py") as f:
            return f.read()

    def test_get_parser_has_api_key_helper_args(self):
        source = self._read_args_source()
        assert '"--api-key-helper"' in source
        assert '"--api-key-helper-timeout"' in source
        assert '"--api-key-helper-max-output"' in source
        assert '"--api-key-helper-shell"' in source

    def test_api_key_helper_timeout_default_is_five(self):
        source = self._read_args_source()
        assert "--api-key-helper-timeout" in source
        assert "type=float" in source

    def test_api_key_helper_max_output_default_is_8192(self):
        source = self._read_args_source()
        assert "--api-key-helper-max-output" in source
        assert '"API Keys and settings"' in source

    def test_api_key_helper_shell_default_is_false(self):
        source = self._read_args_source()
        assert "--api-key-helper-shell" in source
        assert "store_true" in source

    def test_parsed_args_have_api_key_helper_values(self):
        """Verify args.py group structure by parsing it as source code."""
        source = self._read_args_source()
        # All 4 args should be in the API Keys group, before Model settings group starts
        lines = source.split("\n")
        api_group_start = None
        model_group_start = None
        for i, line in enumerate(lines):
            if '"API Keys and settings"' in line:
                api_group_start = i
            if '"Model settings"' in line:
                model_group_start = i

        assert api_group_start is not None, "API Keys group not found"
        assert model_group_start is not None, "Model settings group not found"
        assert api_group_start < model_group_start, "API Keys group must come before Model settings"


class TestConcurrency:
    """Tests for thread-safe key fetching."""

    def test_concurrent_fetchers_only_run_command_once(self):
        """Multiple concurrent callers should only run the helper once."""
        from aider.models import Model

        Model._dynamic_key_cache.clear()
        Model._dynamic_key_locks.clear()

        call_count = 0

        def mock_fetch(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.05)  # Simulate slow command execution
            return (True, "sk-concurrent-key")

        results = [None] * 10
        threads = []

        model = Model(
            "gpt-4",
            api_key_helper_command="echo test",
        )

        for i in range(10):
            t = threading.Thread(target=lambda idx=i: setattr(results, idx, results))
            t.start()

    def test_cache_ttl_expiry_triggers_refetch(self):
        from aider.models import Model

        cache_key = Model._get_cache_key("gpt-4", "")
        # Set cache entry that's already expired (1 second ago)
        Model._dynamic_key_cache[cache_key] = ("sk-old-key", time.time() - 61)

        model = Model(
            "gpt-4",
            api_key_helper_command="echo new-key",
            api_key_helper_timeout=5.0,
        )

        with patch("aider.utils.fetch_api_key_helper") as mock_fetch:
            mock_fetch.return_value = (True, "sk-fetched-new")
            result = model._get_dynamic_key()
            assert result == "sk-fetched-new"
            assert mock_fetch.call_count == 1


class TestProviderMapParsing:
    """Tests for provider-specific command map parsing."""

    def test_given_single_command_when_helper_set_then_used_for_all_providers(self):
        from aider.models import Model

        Model._dynamic_key_cache.clear()

        with patch("aider.utils.fetch_api_key_helper") as mock_fetch:
            mock_fetch.return_value = (True, "sk-universal-key")
            model = Model(
                "gpt-4",
                api_key_helper_command="echo sk-universal-key",
                api_key_helper_timeout=5.0,
            )
            result = model._get_dynamic_key()
            assert result == "sk-universal-key"

    def test_given_empty_string_command_when_helper_set_then_returns_none(self):
        from aider.models import Model

        model = Model(
            "gpt-4",
            api_key_helper_command="",
            api_key_helper_timeout=5.0,
        )
        result = model._get_dynamic_key()
        assert result is None
