import pandas as pd
import requests
import concurrent.futures
import threading
import json
import logging
import os
from typing import Callable, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TabularEnhancer:
    def __init__(self, api_url: str, mapping: Dict[str, str], max_workers: int = 5, auth: Any = None, headers: Dict[str, str] = None):
        """
        :param api_url: The URL of the API to call.
        :param mapping: Dictionary mapping API field names to DataFrame column names.
                        Example: {'user_id': 'id', 'user_name': 'name'}
        :param max_workers: Number of threads for parallel processing.
        :param auth: Optional authentication for the API call (e.g., requests.auth.HTTPBasicAuth).
        :param headers: Optional custom headers for the API call (e.g., for API Key or Bearer Token).
        """
        self.api_url = api_url
        self.mapping = mapping
        self.max_workers = max_workers
        self.auth = auth
        self.headers = headers

    def _prepare_payload(self, row: pd.Series) -> Dict[str, Any]:
        """Constructs the JSON payload from the row based on mapping."""
        payload = {}
        for api_field, col_name in self.mapping.items():
            payload[api_field] = row.get(col_name)
        return payload

    def _process_row(self, index: int, row: pd.Series) -> Dict[str, Any]:
        """Processes a single row: calls API and handles exceptions."""
        result = {'index': index, 'api_response': None, 'exception_summary': None}
        try:
            payload = self._prepare_payload(row)
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=10, 
                auth=self.auth, 
                headers=self.headers
            )
            response.raise_for_status()
            result['api_response'] = response.json()
        except Exception as e:
            logger.error(f"Error processing row {index}: {str(e)}")
            result['exception_summary'] = str(e)
        return result

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Asynchronously processes each row of the DataFrame."""
        results = [None] * len(df)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self._process_row, i, row): i 
                for i, row in df.iterrows()
            }
            
            for future in concurrent.futures.as_completed(future_to_index):
                res = future.result()
                results[res['index']] = res

        # Extract responses and exceptions in the original order
        api_responses = [r['api_response'] for r in results]
        exceptions = [r['exception_summary'] for r in results]
        
        # Add results to DataFrame
        df_enhanced = df.copy()
        df_enhanced['api_response'] = api_responses
        df_enhanced['exception_summary'] = exceptions
        
        return df_enhanced

def read_tabular_file(file_path: str) -> pd.DataFrame:
    """Reads a tabular file (CSV, Excel, etc.) based on its extension, ensuring all data is read as strings."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path, dtype=str)
    elif ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path, dtype=str)
    elif ext == '.tsv':
        return pd.read_csv(file_path, sep='\t', dtype=str)
    elif ext == '.txt':
        # Let Pandas infer the delimiters by setting sep=None and using the python engine.
        return pd.read_csv(file_path, sep=None, engine='python', dtype=str)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def save_tabular_file(df: pd.DataFrame, original_path: str, suffix: str = "_enhanced"):
    """Saves the DataFrame to the same format as the original file."""
    base, ext = os.path.splitext(original_path)
    output_path = f"{base}{suffix}{ext}"
    
    if ext == '.csv':
        df.to_csv(output_path, index=False)
    elif ext in ['.xlsx', '.xls']:
        df.to_excel(output_path, index=False)
    elif ext == '.tsv':
        df.to_csv(output_path, sep='\t', index=False)
    elif ext == '.txt':
        # For saving .txt, default to tab-separated (similar to .tsv)
        df.to_csv(output_path, sep='\t', index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    logger.info(f"Enhanced file saved to: {output_path}")
    return output_path
