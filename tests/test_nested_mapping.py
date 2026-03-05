import unittest
import pandas as pd
from tabular_enhancement_tool.core import TabularEnhancer
from unittest.mock import patch, MagicMock


class TestNestedMapping(unittest.TestCase):
    def test_nested_mapping_payload(self):
        # The mapping from the issue description
        mapping = {
            "personId": "identifier",
            "address": [{"street1": "street", "city": "city", "zip_code": "zip"}],
        }

        # Sample row from DataFrame
        row = pd.Series(
            {
                "identifier": "123",
                "street": "Main St",
                "city": "Springfield",
                "zip": "62704",
            }
        )

        enhancer = TabularEnhancer(api_url="http://api.example.com", mapping=mapping)

        # Test _prepare_payload
        payload = enhancer._prepare_payload(row)

        expected_payload = {
            "personId": "123",
            "address": [
                {"street1": "Main St", "city": "Springfield", "zip_code": "62704"}
            ],
        }

        self.assertEqual(payload, expected_payload)

    def test_nested_mapping_get_params(self):
        # Mapping for GET with nesting
        mapping = {
            "id": "identifier",
            "extra": {"category": "cat", "tags": ["tag1", "tag2"]},
        }

        row = pd.Series(
            {"identifier": "123", "cat": "book", "tag1": "fiction", "tag2": "mystery"}
        )

        enhancer = TabularEnhancer(
            api_url="http://api.example.com", mapping=mapping, method="GET"
        )

        # For GET, _process_row is called, which calls _prepare_payload
        # Let's mock requests.get
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "ok"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            enhancer._process_row(0, row)

            # Check what was passed to requests.get
            args, kwargs = mock_get.call_args
            # params should contain the nested payload
            expected_params = {
                "id": "123",
                "extra": {"category": "book", "tags": ["fiction", "mystery"]},
            }
            self.assertEqual(kwargs["params"], expected_params)


if __name__ == "__main__":
    unittest.main()
