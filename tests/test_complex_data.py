import unittest
import pandas as pd
import os
import shutil
import numpy as np
from unittest.mock import patch, MagicMock
from tabular_enhancement_tool.core import TabularEnhancer, read_tabular_file, save_tabular_file

class TestComplexData(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_complex_files"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_simulated_titanic_dataset(self):
        # Create a simulated Titanic-like dataset with mixed types and missing values
        # Since pandas 3.0.1 is used, we ensure data integrity by treating all as str
        titanic_data = {
            "PassengerId": ["1", "2", "3", "4", "5"],
            "Survived": ["0", "1", "1", "0", "0"],
            "Pclass": ["3", "1", "3", "1", "3"],
            "Name": ["Braund, Mr. Owen Harris", "Cumings, Mrs. John Bradley (Florence Briggs Thayer)", "Heikkinen, Miss. Laina", "Futrelle, Mrs. Jacques Heath (Lily May Peel)", "Allen, Mr. William Henry"],
            "Sex": ["male", "female", "female", "female", "male"],
            "Age": ["22", "38", "26", "35", "nan"], # Using 'nan' as string for consistency
            "Fare": ["7.25", "71.2833", "7.925", "53.1", "8.05"]
        }
        df_titanic = pd.DataFrame(titanic_data)
        csv_path = os.path.join(self.test_dir, "titanic.csv")
        df_titanic.to_csv(csv_path, index=False)
        
        # Test reading
        df_loaded = read_tabular_file(csv_path)
        # All columns should be strings (object or string dtype in Pandas 3)
        for col in df_loaded.columns:
            self.assertTrue(pd.api.types.is_object_dtype(df_loaded[col]) or pd.api.types.is_string_dtype(df_loaded[col]))
        
        # Test enhancement
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"processed": True}
            mock_post.return_value = mock_response
            
            mapping = {"id": "PassengerId", "name": "Name"}
            enhancer = TabularEnhancer("http://api.example.com", mapping)
            df_enhanced = enhancer.process_dataframe(df_loaded)
            
            self.assertEqual(len(df_enhanced), 5)
            self.assertIn("api_response", df_enhanced.columns)
            self.assertEqual(df_enhanced.loc[0, "api_response"], {"processed": True})

    def test_simulated_iris_dataset(self):
        # Iris-like dataset with floating point values
        iris_data = {
            "sepal_length": ["5.1", "4.9", "4.7", "4.6", "5.0"],
            "sepal_width": ["3.5", "3.0", "3.2", "3.1", "3.6"],
            "petal_length": ["1.4", "1.4", "1.3", "1.5", "1.4"],
            "petal_width": ["0.2", "0.2", "0.2", "0.2", "0.2"],
            "species": ["setosa", "setosa", "setosa", "setosa", "setosa"]
        }
        df_iris = pd.DataFrame(iris_data)
        xlsx_path = os.path.join(self.test_dir, "iris.xlsx")
        df_iris.to_excel(xlsx_path, index=False)
        
        df_loaded = read_tabular_file(xlsx_path)
        # Check that floating points were not coerced to floats but kept as strings
        self.assertEqual(df_loaded.loc[0, "sepal_length"], "5.1")
        
        # Test saving back
        new_path = save_tabular_file(df_loaded, xlsx_path, suffix="_new")
        df_reloaded = read_tabular_file(new_path)
        pd.testing.assert_frame_equal(df_loaded, df_reloaded)

    def test_unicode_and_special_chars(self):
        # Dataset with Unicode and special characters to test robustness
        data = {
            "id": ["1", "2"],
            "text": ["Héllo World", "Ω Mega"],
            "symbol": ["$100", "€50"],
            "mixed": ["007", "1.2.3"]
        }
        df = pd.DataFrame(data)
        tsv_path = os.path.join(self.test_dir, "unicode.tsv")
        df.to_csv(tsv_path, sep='\t', index=False)
        
        df_loaded = read_tabular_file(tsv_path)
        self.assertEqual(df_loaded.loc[0, "text"], "Héllo World")
        self.assertEqual(df_loaded.loc[1, "text"], "Ω Mega")
        self.assertEqual(df_loaded.loc[0, "mixed"], "007")

        # Test enhancement with unicode data
        with patch('requests.post') as mock_post:
            def side_effect(url, json=None, **kwargs):
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {"echo": json}
                return mock_resp
            mock_post.side_effect = side_effect
            
            mapping = {"content": "text", "val": "mixed"}
            enhancer = TabularEnhancer("http://api.example.com", mapping)
            df_enhanced = enhancer.process_dataframe(df_loaded)
            
            self.assertEqual(df_enhanced.loc[0, "api_response"]["echo"]["content"], "Héllo World")
            self.assertEqual(df_enhanced.loc[0, "api_response"]["echo"]["val"], "007")

if __name__ == '__main__':
    unittest.main()
