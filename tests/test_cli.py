import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd
import shutil
from tabular_enhancement_tool.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_cli_files"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.csv_path = os.path.join(self.test_dir, "test.csv")
        pd.DataFrame({"id": [1], "name": ["Alice"]}).to_csv(self.csv_path, index=False)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("tabular_enhancement_tool.core.TabularEnhancer.process_dataframe")
    @patch("tabular_enhancement_tool.core.save_tabular_file")
    def test_cli_basic_execution(self, mock_save, mock_process):
        mock_process.return_value = pd.DataFrame(
            {
                "id": [1],
                "name": ["Alice"],
                "status": ["ok"],
                "exception_summary": [None],
            }
        )
        mock_save.return_value = "test_enhanced.csv"

        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"api_id": "id"}',
        ]
        with patch.object(sys, "argv", test_args):
            main()

        mock_process.assert_called_once()
        mock_save.assert_called_once()

    @patch("tabular_enhancement_tool.core.TabularEnhancer.process_dataframe")
    @patch("tabular_enhancement_tool.core.save_tabular_file")
    def test_cli_no_flatten(self, mock_save, mock_process):
        mock_process.return_value = pd.DataFrame(
            {
                "id": [1],
                "name": ["Alice"],
                "api_response": [{"status": "ok"}],
                "exception_summary": [None],
            }
        )
        mock_save.return_value = "test_enhanced.csv"

        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"api_id": "id"}',
            "--no_flatten",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        mock_process.assert_called_once()
        # Verify that enhancer was called with flatten_response=False
        # Since we patched process_dataframe, we need to find where enhancer was created.
        # It might be easier to patch TabularEnhancer class.

    @patch("sys.exit")
    def test_cli_invalid_json_mapping(self, mock_exit):
        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            "invalid_json",
        ]
        with patch.object(sys, "argv", test_args):
            # We expect it to print an error and exit
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("Error: Invalid JSON mapping string.")
                mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_cli_no_urls(self, mock_exit):
        test_args = ["cli.py", self.csv_path]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("Error: --api_url is required.")
                mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_cli_api_no_mapping(self, mock_exit):
        test_args = ["cli.py", self.csv_path, "--api_url", "http://api.example.com"]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call(
                    "Error: --mapping is required for API enhancement."
                )
                mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_cli_api_mapping_not_dict(self, mock_exit):
        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '["not", "a", "dict"]',
        ]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call(
                    "Error: --mapping must be a JSON object for API enhancement."
                )
                mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_cli_auth_basic_missing_creds(self, mock_exit):
        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"a": "b"}',
            "--auth_type",
            "basic",
        ]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call(
                    "Error: --auth_user and --auth_pass are required for basic auth."
                )
                mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_cli_auth_bearer_missing_token(self, mock_exit):
        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"a": "b"}',
            "--auth_type",
            "bearer",
        ]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call(
                    "Error: --auth_token is required for bearer auth."
                )
                mock_exit.assert_called_with(1)

    @patch("sys.exit")
    def test_cli_auth_apikey_missing_token(self, mock_exit):
        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"a": "b"}',
            "--auth_type",
            "apikey",
        ]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call(
                    "Error: --auth_token is required for apikey auth."
                )
                mock_exit.assert_called_with(1)

    def test_cli_main_entry(self):
        """Test the if __name__ == '__main__': block in cli.py."""
        import runpy
        import os

        # Use a real file path for input_file because cli.py checks for it
        dummy_file = "dummy_entry.csv"
        with open(dummy_file, "w") as f:
            f.write("a,b\n1,2")

        try:
            # We don't patch 'tabular_enhancement_tool.cli.main' because runpy executes the module code
            # and it will call the ACTUAL main() function defined in that module instance.
            # Instead, we patch the 'main' that is in the namespace of the module being executed.
            with patch(
                "tabular_enhancement_tool.cli.tet.read_tabular_file"
            ) as mock_read:
                mock_read.return_value = pd.DataFrame({"a": [1]})
                with patch("tabular_enhancement_tool.cli.tet.save_tabular_file"):
                    with patch(
                        "tabular_enhancement_tool.cli.tet.TabularEnhancer"
                    ) as mock_enhancer_cls:
                        test_args = [
                            "cli.py",
                            dummy_file,
                            "--api_url",
                            "http://api.com",
                            "--mapping",
                            '{"a":"a"}',
                        ]
                        with patch("sys.argv", test_args):
                            runpy.run_module(
                                "tabular_enhancement_tool.cli", run_name="__main__"
                            )
                            # If it reached here without error, the __main__ block executed main()
                            mock_enhancer_cls.assert_called_once()
        finally:
            if os.path.exists(dummy_file):
                os.remove(dummy_file)

    @patch("sys.exit")
    def test_cli_input_file_not_found(self, mock_exit):
        test_args = [
            "cli.py",
            "non_existent.csv",
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"a": "b"}',
        ]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("Error: File non_existent.csv not found.")
                mock_exit.assert_called_with(1)

    @patch("tabular_enhancement_tool.core.TabularEnhancer")
    @patch("tabular_enhancement_tool.core.read_tabular_file")
    @patch("tabular_enhancement_tool.core.save_tabular_file")
    def test_cli_auth_basic(self, mock_save, mock_read, mock_enhancer_cls):
        mock_read.return_value = pd.DataFrame({"id": [1]})
        mock_enhancer = MagicMock()
        mock_enhancer_cls.return_value = mock_enhancer

        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"api_id": "id"}',
            "--auth_type",
            "basic",
            "--auth_user",
            "user",
            "--auth_pass",
            "pass",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify HTTPBasicAuth was created and passed
        from requests.auth import HTTPBasicAuth

        args, kwargs = mock_enhancer_cls.call_args
        self.assertIsInstance(kwargs["auth"], HTTPBasicAuth)
        self.assertEqual(kwargs["auth"].username, "user")
        self.assertEqual(kwargs["auth"].password, "pass")

    @patch("tabular_enhancement_tool.core.TabularEnhancer")
    @patch("tabular_enhancement_tool.core.read_tabular_file")
    @patch("tabular_enhancement_tool.core.save_tabular_file")
    def test_cli_auth_bearer(self, mock_save, mock_read, mock_enhancer_cls):
        mock_read.return_value = pd.DataFrame({"id": [1]})
        mock_enhancer = MagicMock()
        mock_enhancer_cls.return_value = mock_enhancer

        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"api_id": "id"}',
            "--auth_type",
            "bearer",
            "--auth_token",
            "my_token",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        args, kwargs = mock_enhancer_cls.call_args
        self.assertEqual(kwargs["headers"], {"Authorization": "Bearer my_token"})

    @patch("tabular_enhancement_tool.core.TabularEnhancer")
    @patch("tabular_enhancement_tool.core.read_tabular_file")
    @patch("tabular_enhancement_tool.core.save_tabular_file")
    def test_cli_auth_apikey(self, mock_save, mock_read, mock_enhancer_cls):
        mock_read.return_value = pd.DataFrame({"id": [1]})
        mock_enhancer = MagicMock()
        mock_enhancer_cls.return_value = mock_enhancer

        test_args = [
            "cli.py",
            self.csv_path,
            "--api_url",
            "http://api.example.com",
            "--mapping",
            '{"api_id": "id"}',
            "--auth_type",
            "apikey",
            "--auth_token",
            "my_key",
            "--auth_header",
            "X-Custom-Key",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        args, kwargs = mock_enhancer_cls.call_args
        self.assertEqual(kwargs["headers"], {"X-Custom-Key": "my_key"})


if __name__ == "__main__":
    unittest.main()
