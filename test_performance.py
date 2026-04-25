"""
Tests for performance improvements in the AI app.

Goals:
- Verify the OpenAI client is initialized once at module import time and reused by ask_gpt.
- Prefer deterministic behavioral tests over wall-clock timing benchmarks.
- Keep filesystem tests reliable across OS/CI environments.
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import time
import unittest
from unittest import mock


def _fresh_import(module_name: str):
    """Import a module from scratch (bypassing any cached sys.modules entry)."""
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)


class TestAppPerformance(unittest.TestCase):
    """Tests performance-related behavior in app.py"""

    def _make_mock_response(self, content: str = "Test response"):
        mock_response = mock.MagicMock()
        mock_response.choices = [mock.MagicMock()]
        mock_response.choices[0].message.content = content
        return mock_response

    @mock.patch("app.OpenAI")
    def test_client_initialized_once_at_import_and_reused(self, mock_openai):
        """OpenAI client should be constructed once at module import and reused."""
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = self._make_mock_response()

        # Fresh import so module-level client initialization happens under our patch.
        app_module = _fresh_import("app")

        # Client constructed once at import time
        mock_openai.assert_called_once()

        # Multiple calls should not reconstruct the client
        app_module.ask_gpt("test 1")
        app_module.ask_gpt("test 2")
        app_module.ask_gpt("test 3")
        mock_openai.assert_called_once()

        # But API calls should be routed through the one shared client
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)

    @mock.patch("app.OpenAI")
    def test_api_calls_use_same_client_instance(self, mock_openai):
        """All ask_gpt calls should use the same mock client instance."""
        mock_client = mock.MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = self._make_mock_response("Response")

        app_module = _fresh_import("app")

        for i in range(5):
            app_module.ask_gpt(f"prompt {i}")

        self.assertEqual(mock_client.chat.completions.create.call_count, 5)

        # Optional: verify the prompts were passed through
        calls = mock_client.chat.completions.create.call_args_list
        for i, call in enumerate(calls):
            kwargs = call.kwargs
            self.assertEqual(kwargs["model"], "gpt-3.5-turbo")
            self.assertEqual(kwargs["messages"], [{"role": "user", "content": f"prompt {i}"}])


class TestDownloadScriptPerformance(unittest.TestCase):
    """Filesystem behavior tests (scandir usage pattern)."""

    def test_scandir_lists_files_and_sizes(self):
        """Validate scandir-based listing returns correct file sizes."""
        with tempfile.TemporaryDirectory() as test_dir:
            for i in range(10):
                filepath = os.path.join(test_dir, f"test_file_{i}.csv")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("x" * (100 * (i + 1)))

            files_found = []
            with os.scandir(test_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        size = entry.stat().st_size
                        files_found.append((entry.name, size))

            self.assertEqual(len(files_found), 10)

            for name, size in files_found:
                idx = int(name.split("_")[2].split(".")[0])
                expected_size = 100 * (idx + 1)
                self.assertEqual(size, expected_size)

    def test_scandir_error_handling_missing_dir(self):
        """scandir should raise when directory does not exist (portable path)."""
        # Create then remove a directory to guarantee a non-existent path on all OSes
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "definitely_missing")

        with self.assertRaises(OSError):
            with os.scandir(missing) as entries:
                list(entries)


class TestPerformanceComparison(unittest.TestCase):
    """Lightweight comparison test (kept non-failing; prints only)."""

    @unittest.skipUnless(
        os.environ.get("RUN_BENCHMARKS") == "1",
        "Set RUN_BENCHMARKS=1 to run timing benchmarks (skipped in CI by default).",
    )
    def test_file_listing_performance_benchmark(self):
        """Optional benchmark comparing os.listdir vs os.scandir (non-deterministic)."""
        with tempfile.TemporaryDirectory() as test_dir:
            for i in range(2000):
                filepath = os.path.join(test_dir, f"file_{i}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("data")

            start_old = time.perf_counter()
            files_old = []
            for file in os.listdir(test_dir):
                file_path = os.path.join(test_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    files_old.append((file, size))
            time_old = time.perf_counter() - start_old

            start_new = time.perf_counter()
            files_new = []
            with os.scandir(test_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        size = entry.stat().st_size
                        files_new.append((entry.name, size))
            time_new = time.perf_counter() - start_new

            self.assertEqual(len(files_old), len(files_new))

            print("\nPerformance comparison:")
            print(f"  os.listdir approach: {time_old:.6f}s")
            print(f"  os.scandir approach: {time_new:.6f}s")
            if time_new > 0:
                print(f"  Speedup: {time_old / time_new:.2f}x")
            else:
                print("  Speedup: N/A (time_new too small)")


if __name__ == "__main__":
    unittest.main()
