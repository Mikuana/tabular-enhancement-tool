import unittest
import pandas as pd
import os
import shutil
from unittest.mock import patch, MagicMock
from tabular_enhancement_tool.core import TabularEnhancer, read_tabular_file, save_tabular_file

class TestCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_files"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        self.csv_path = os.path.join(self.test_dir, "test.csv")
        self.tsv_path = os.path.join(self.test_dir, "test.tsv")
        self.xlsx_path = os.path.join(self.test_dir, "test.xlsx")
        self.txt_comma_path = os.path.join(self.test_dir, "test_comma.txt")
        self.txt_tab_path = os.path.join(self.test_dir, "test_tab.txt")
        self.txt_pipe_path = os.path.join(self.test_dir, "test_pipe.txt")
        
        self.df = pd.DataFrame({
            "id": ["01", "02", "03"],
            "name": ["Alice", "Bob", "Charlie"]
        })
        self.df.to_csv(self.csv_path, index=False)
        self.df.to_csv(self.tsv_path, sep='\t', index=False)
        self.df.to_excel(self.xlsx_path, index=False)
        self.df.to_csv(self.txt_comma_path, index=False)
        self.df.to_csv(self.txt_tab_path, sep='\t', index=False)
        self.df.to_csv(self.txt_pipe_path, sep='|', index=False)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_read_tabular_file_csv(self):
        df = read_tabular_file(self.csv_path)
        pd.testing.assert_frame_equal(df, self.df)

    def test_read_tabular_file_tsv(self):
        df = read_tabular_file(self.tsv_path)
        pd.testing.assert_frame_equal(df, self.df)

    def test_read_tabular_file_xlsx(self):
        df = read_tabular_file(self.xlsx_path)
        pd.testing.assert_frame_equal(df, self.df)

    def test_read_tabular_file_txt_comma(self):
        df = read_tabular_file(self.txt_comma_path)
        pd.testing.assert_frame_equal(df, self.df)

    def test_read_tabular_file_txt_tab(self):
        df = read_tabular_file(self.txt_tab_path)
        pd.testing.assert_frame_equal(df, self.df)

    def test_read_tabular_file_txt_pipe(self):
        df = read_tabular_file(self.txt_pipe_path)
        pd.testing.assert_frame_equal(df, self.df)

    def test_read_tabular_file_unsupported(self):
        with self.assertRaises(ValueError):
            read_tabular_file("test.invalid")

    def test_save_tabular_file_csv(self):
        save_path = save_tabular_file(self.df, self.csv_path, suffix="_new")
        self.assertTrue(os.path.exists(save_path))
        self.assertIn("_new.csv", save_path)
        df_loaded = pd.read_csv(save_path, dtype=str)
        pd.testing.assert_frame_equal(df_loaded, self.df)

    def test_save_tabular_file_tsv(self):
        save_path = save_tabular_file(self.df, self.tsv_path, suffix="_new")
        self.assertTrue(os.path.exists(save_path))
        self.assertIn("_new.tsv", save_path)
        df_loaded = pd.read_csv(save_path, sep='\t', dtype=str)
        pd.testing.assert_frame_equal(df_loaded, self.df)

    def test_save_tabular_file_xlsx(self):
        save_path = save_tabular_file(self.df, self.xlsx_path, suffix="_new")
        self.assertTrue(os.path.exists(save_path))
        self.assertIn("_new.xlsx", save_path)
        df_loaded = pd.read_excel(save_path, dtype=str)
        pd.testing.assert_frame_equal(df_loaded, self.df)

    def test_save_tabular_file_txt(self):
        save_path = save_tabular_file(self.df, self.txt_comma_path, suffix="_new")
        self.assertTrue(os.path.exists(save_path))
        self.assertIn("_new.txt", save_path)
        # We specified it should save as tab-separated
        df_loaded = pd.read_csv(save_path, sep='\t', dtype=str)
        pd.testing.assert_frame_equal(df_loaded, self.df)

    def test_save_tabular_file_unsupported(self):
        with self.assertRaises(ValueError):
            save_tabular_file(self.df, "test.invalid")

    @patch('requests.post')
    def test_tabular_enhancer_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        mapping = {"api_id": "id", "api_name": "name"}
        enhancer = TabularEnhancer("http://api.example.com", mapping)
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(len(df_enhanced), 3)
        self.assertIn('api_response', df_enhanced.columns)
        self.assertIn('exception_summary', df_enhanced.columns)
        for response in df_enhanced['api_response']:
            self.assertEqual(response, {"status": "ok"})
        for exc in df_enhanced['exception_summary']:
            self.assertTrue(pd.isna(exc))

    @patch('requests.post')
    def test_tabular_enhancer_api_error(self, mock_post):
        def side_effect(*args, **kwargs):
            payload = kwargs.get('json')
            if payload and payload.get('api_id') == "02":
                mock_resp = MagicMock()
                mock_resp.status_code = 500
                mock_resp.raise_for_status.side_effect = Exception("API Error")
                return mock_resp
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"status": "ok"}
            return mock_resp

        mock_post.side_effect = side_effect

        mapping = {"api_id": "id", "api_name": "name"}
        enhancer = TabularEnhancer("http://api.example.com", mapping)
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(df_enhanced.loc[1, 'exception_summary'], "API Error")
        self.assertTrue(pd.isna(df_enhanced.loc[0, 'exception_summary']))
        self.assertTrue(pd.isna(df_enhanced.loc[2, 'exception_summary']))

    @patch('requests.post')
    def test_tabular_enhancer_empty_dataframe(self, mock_post):
        df_empty = pd.DataFrame(columns=["id", "name"])
        mapping = {"api_id": "id"}
        enhancer = TabularEnhancer("http://api.example.com", mapping)
        df_enhanced = enhancer.process_dataframe(df_empty)
        self.assertEqual(len(df_enhanced), 0)
        self.assertIn('api_response', df_enhanced.columns)
        self.assertIn('exception_summary', df_enhanced.columns)

    @patch('requests.post')
    def test_tabular_enhancer_order_preservation(self, mock_post):
        # Use a longer dataframe to better test concurrency issues
        df_large = pd.DataFrame({"id": [str(i).zfill(2) for i in range(20)]})
        
        # Simulate varying response times
        import time
        import random
        def side_effect(*args, **kwargs):
            time.sleep(random.uniform(0.01, 0.05))
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"id": kwargs['json']['api_id']}
            return mock_resp
            
        mock_post.side_effect = side_effect
        
        mapping = {"api_id": "id"}
        enhancer = TabularEnhancer("http://api.example.com", mapping, max_workers=5)
        df_enhanced = enhancer.process_dataframe(df_large)
        
        self.assertEqual(df_enhanced["id"].tolist(), [str(i).zfill(2) for i in range(20)])
        for i, row in df_enhanced.iterrows():
            self.assertEqual(row['api_response']['id'], row['id'])

if __name__ == '__main__':
    unittest.main()
