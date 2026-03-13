import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from tabular_enhancement_tool.core import TabularEnhancer


class TestComplexNestedMapping(unittest.TestCase):
    def test_deeply_nested_mapping(self):
        """Test deeply nested structures with mixed types and columns."""
        mapping = {
            "level1": {
                "level2": [
                    {"level3_a": "col_a"},
                    {"level3_b": ["col_b", 12345]},
                    "col_c",
                ],
                "fixed_level2": 123,
            }
        }
        df = pd.DataFrame(
            {"col_a": ["a1", "a2"], "col_b": ["b1", "b2"], "col_c": ["c1", "c2"]}
        )
        enhancer = TabularEnhancer("http://api.com", mapping)

        payload1 = enhancer._prepare_payload(df.iloc[0])
        expected1 = {
            "level1": {
                "level2": [{"level3_a": "a1"}, {"level3_b": ["b1", 12345]}, "c1"],
                "fixed_level2": 123,
            }
        }
        self.assertEqual(payload1, expected1)

        payload2 = enhancer._prepare_payload(df.iloc[1])
        expected2 = {
            "level1": {
                "level2": [{"level3_a": "a2"}, {"level3_b": ["b2", 12345]}, "c2"],
                "fixed_level2": 123,
            }
        }
        self.assertEqual(payload2, expected2)

    def test_empty_structures_in_mapping(self):
        """Test empty dicts and lists in mapping."""
        mapping = {
            "empty_dict": {},
            "empty_list": [],
            "nested_empty": {"d": {}, "l": []},
            "id": "id",
        }
        df = pd.DataFrame({"id": ["1"]})
        enhancer = TabularEnhancer("http://api.com", mapping)
        payload = enhancer._prepare_payload(df.iloc[0])

        expected = {
            "empty_dict": {},
            "empty_list": [],
            "nested_empty": {"d": {}, "l": []},
            "id": "1",
        }
        self.assertEqual(payload, expected)

    @patch("requests.post")
    def test_nested_get_params_in_post_method(self, mock_post):
        """Verify that POST method uses the nested structure in JSON body."""
        mapping = {
            "query": {
                "filters": [
                    {"field": 123, "value": "v1"},
                    {"field": 456, "value": "v2"},
                ]
            }
        }
        # mapping fixed integers for field
        # but tet treats strings as columns if they exist.
        df = pd.DataFrame({"v1": ["val1"], "v2": ["val2"]})

        enhancer = TabularEnhancer("http://api.com", mapping, method="POST")

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        enhancer.process_dataframe(df)

        expected_json = {
            "query": {
                "filters": [
                    {"field": 123, "value": "val1"},
                    {"field": 456, "value": "val2"},
                ]
            }
        }
        mock_post.assert_called_with(
            "http://api.com",
            json=expected_json,
            params=None,
            timeout=10,
            auth=None,
            headers={"Content-Type": "application/json"},
            cert=None,
        )


if __name__ == "__main__":
    unittest.main()
