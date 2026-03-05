import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
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


if __name__ == "__main__":
    unittest.main()
