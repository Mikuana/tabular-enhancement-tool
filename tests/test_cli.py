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
                "api_response": [{}],
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
