import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from tabular_enhancement_tool.core import BaseEnhancer, TabularEnhancer


class TestCoverageExpansion(unittest.TestCase):
    def test_base_enhancer_not_implemented(self):
        """Test that BaseEnhancer._process_row raises NotImplementedError."""
        enhancer = BaseEnhancer()
        with self.assertRaises(NotImplementedError):
            enhancer._process_row(0, pd.Series({"a": 1}))

    def test_tabular_enhancer_prepare_payload_non_string_val(self):
        """Test fallback for non-str/dict/list values in mapping (Line 132)."""
        mapping = {
            "int_val": 123,
            "float_val": 45.6,
            "bool_val": True,
            "none_val": None,
            "nested": [1, {"a": 2}],
        }
        enhancer = TabularEnhancer("http://api.com", mapping)
        row = pd.Series({"some_col": "some_val"})
        payload = enhancer._prepare_payload(row)

        self.assertEqual(payload["int_val"], 123)
        self.assertEqual(payload["float_val"], 45.6)
        self.assertEqual(payload["bool_val"], True)
        self.assertEqual(payload["none_val"], None)
        self.assertEqual(payload["nested"][0], 1)
        self.assertEqual(payload["nested"][1]["a"], 2)

    @patch("requests.get")
    def test_tabular_enhancer_get_url_format_failure(self, mock_get):
        """Test URL formatting failure fallback (Lines 160-163)."""
        # Scenario: URL has placeholders but they don't match payload keys
        # Actually, .format() raises KeyError if a key is missing in kwargs.
        # But the code tries to find placeholders and pop them from params.

        # If we have a placeholder that is NOT in the payload,
        # format_dict will not have it, and .format(**format_dict) will raise KeyError.

        api_url = "http://api.com/{missing_key}"
        mapping = {"id": "id"}  # payload will have {"id": "..."}
        enhancer = TabularEnhancer(api_url, mapping, method="GET")
        row = pd.Series({"id": "1"})

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        # This should trigger the try-except block in _process_row
        result = enhancer._process_row(0, row)

        # Verify it fell back to using the original api_url and all payload as params
        # The code does:
        # url = self.api_url
        # params = payload
        mock_get.assert_called_with(
            api_url, params={"id": "1"}, timeout=10, auth=None, headers=None
        )
        self.assertEqual(result["response"], {"status": "ok"})

    def test_read_tabular_file_sniff_failure(self):
        """Test fallback when Sniffer fails."""
        import os

        test_file = "test_sniff_fail.txt"
        with open(test_file, "w") as f:
            # Provide a sample that is likely to fail sniffing
            f.write("Just some text")
        try:
            # Sniffer might still "find" a delimiter (like space),
            # so we mock Sniffer.sniff to raise an error.
            with patch("csv.Sniffer.sniff") as mock_sniff:
                mock_sniff.side_effect = Exception("Sniff failed")
                enhancer = TabularEnhancer(file_path=test_file)
                enhancer.read()
                self.assertEqual(enhancer.sep, ",")

            # Test .tsv fallback
            tsv_file = "test_sniff.tsv"
            with open(tsv_file, "w") as f:
                f.write("a\tb")
            try:
                with patch("csv.Sniffer.sniff") as mock_sniff:
                    mock_sniff.side_effect = Exception("Sniff failed")
                    enhancer = TabularEnhancer(file_path=tsv_file)
                    enhancer.read()
                    self.assertEqual(enhancer.sep, "\t")
            finally:
                if os.path.exists(tsv_file):
                    os.remove(tsv_file)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_save_tabular_file_tsv_default_sep(self):
        """Test save for .tsv without explicit sep."""
        import os

        tsv_path = "test_default.tsv"
        try:
            df = pd.DataFrame({"a": ["1"]})
            enhancer = TabularEnhancer(file_path=tsv_path)
            enhancer.df = df
            output_path = enhancer.save()
            self.assertTrue(os.path.exists(output_path))
            # Verify it saved with tab
            with open(output_path, "r") as f:
                self.assertEqual(
                    f.read().strip(), "a\n1"
                )  # No tab if only one column, but let's check sep
            # If we had two columns:
            df2 = pd.DataFrame({"a": ["1"], "b": ["2"]})
            enhancer2 = TabularEnhancer(file_path=tsv_path)
            enhancer2.df = df2
            output_path2 = enhancer2.save()
            with open(output_path2, "r") as f:
                self.assertIn("\t", f.read())
        finally:
            if os.path.exists(tsv_path):
                os.remove(tsv_path)
            enhanced = tsv_path.replace(".tsv", "_enhanced.tsv")
            if os.path.exists(enhanced):
                os.remove(enhanced)

    def test_save_tabular_file_txt_default_sep(self):
        """Test save for .txt without explicit sep."""
        import os

        df = pd.DataFrame({"a": ["1"], "b": ["2"]})
        txt_path = "test_default.txt"
        try:
            enhancer = TabularEnhancer(file_path=txt_path)
            enhancer.df = df
            output_path = enhancer.save()
            self.assertTrue(os.path.exists(output_path))
            # Verify it saved with comma (default for txt)
            with open(output_path, "r") as f:
                self.assertIn(",", f.read())
        finally:
            if os.path.exists(txt_path):
                os.remove(txt_path)
            enhanced = txt_path.replace(".txt", "_enhanced.txt")
            if os.path.exists(enhanced):
                os.remove(enhanced)

    def test_save_tabular_file_unsupported_exception(self):
        """Test save unsupported format exception."""
        df = pd.DataFrame({"a": ["1"]})
        enhancer = TabularEnhancer(file_path="test.invalid_ext")
        enhancer.df = df
        with self.assertRaises(ValueError):
            enhancer.save()

    def test_tabular_enhancer_missing_config_errors(self):
        """Test error handling in TabularEnhancer."""
        # No file_path for read
        enhancer = TabularEnhancer()
        with self.assertRaises(ValueError):
            enhancer.read()

        # No df for enhance
        with self.assertRaises(ValueError):
            enhancer.enhance()

        # No config for enhance
        enhancer.df = pd.DataFrame({"a": [1]})
        with self.assertRaises(ValueError):
            enhancer.enhance()

        # No df for save
        enhancer.df = None
        with self.assertRaises(ValueError):
            enhancer.save()

        # No file_path for save
        enhancer.df = pd.DataFrame({"a": [1]})
        with self.assertRaises(ValueError):
            enhancer.save()

    def test_tabular_enhancer_full_workflow(self):
        """Test full workflow using unified TabularEnhancer class."""
        import os

        test_file = "workflow.csv"
        df = pd.DataFrame({"id": ["1", "2"]})
        df.to_csv(test_file, index=False)
        try:
            with patch("requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "ok"}
                mock_post.return_value = mock_response

                enhancer = TabularEnhancer(
                    file_path=test_file,
                    api_url="http://api.com",
                    mapping={"id": "id"},
                )
                df_read = enhancer.read()
                self.assertEqual(len(df_read), 2)

                df_enhanced = enhancer.enhance()
                self.assertIn("status", df_enhanced.columns)

                save_path = enhancer.save()
                self.assertTrue(os.path.exists(save_path))
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
            enhanced = test_file.replace(".csv", "_enhanced.csv")
            if os.path.exists(enhanced):
                os.remove(enhanced)


if __name__ == "__main__":
    unittest.main()
