import pandas as pd
import requests
import concurrent.futures
import logging
import os
import re
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseEnhancer:
    """Base class for enhancing DataFrames asynchronously."""

    def __init__(
        self,
        max_workers: int = 5,
        flatten_response: bool = True,
        response_column_name: str = "response",
    ):
        self.max_workers = max_workers
        self.flatten_response = flatten_response
        self.response_column_name = response_column_name

    def _process_row(self, index: int, row: pd.Series) -> Dict[str, Any]:
        """Processes a single row. Must be implemented by subclasses."""
        raise NotImplementedError

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Asynchronously processes each row of the DataFrame."""
        results = [None] * len(df)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            future_to_index = {
                executor.submit(self._process_row, i, row): i
                for i, row in df.iterrows()
            }

            for future in concurrent.futures.as_completed(future_to_index):
                res = future.result()
                results[res["index"]] = res

        # Extract responses and exceptions in the original order
        responses = [r["response"] for r in results]
        exceptions = [r["exception_summary"] for r in results]

        # Add results to DataFrame
        df_enhanced = df.copy()

        if self.flatten_response:
            # Expand dictionaries in 'responses' to individual columns
            # Ensure each response is a dictionary for expansion
            expanded_responses = []
            for r in responses:
                if isinstance(r, dict):
                    expanded_responses.append(r)
                else:
                    # If not a dict (e.g. None due to error), use empty dict
                    expanded_responses.append({})

            res_df = pd.DataFrame(expanded_responses, index=df.index)
            # Add a prefix to avoid collision?
            # The issue says "applied to the enhanced file as individual columns"
            # It doesn't specify prefix. Let's not add prefix unless needed.
            df_enhanced = pd.concat([df_enhanced, res_df], axis=1)
        else:
            df_enhanced[self.response_column_name] = responses

        df_enhanced["exception_summary"] = exceptions

        return df_enhanced


class TabularEnhancer(BaseEnhancer):
    def __init__(
        self,
        api_url: str,
        mapping: Dict[str, str],
        max_workers: int = 5,
        auth: Any = None,
        headers: Dict[str, str] = None,
        method: str = "POST",
        flatten_response: bool = True,
        response_column_name: str = "api_response",
    ):
        """
        :param api_url: The URL of the API to call. Can contain placeholders for GET requests.
        :param mapping: Dictionary mapping API field names to DataFrame column names.
                        Example: {'user_id': 'id', 'user_name': 'name'}
        :param max_workers: Number of threads for parallel processing.
        :param auth: Optional authentication for the API call (e.g., requests.auth.HTTPBasicAuth).
        :param headers: Optional custom headers for the API call (e.g., for API Key or Bearer Token).
        :param method: HTTP method to use (POST or GET).
        :param flatten_response: Whether to expand the response into individual columns (default: True).
        :param response_column_name: Name of the response column when flattening is disabled (default: 'api_response').
        """
        super().__init__(
            max_workers=max_workers,
            flatten_response=flatten_response,
            response_column_name=response_column_name,
        )
        self.api_url = api_url
        self.mapping = mapping
        self.auth = auth
        self.headers = headers
        self.method = method.upper()
        self._missing_cols_warned = set()

    def _prepare_payload(self, row: pd.Series) -> Dict[str, Any]:
        """Constructs the JSON payload from the row based on mapping."""

        def _get_value(mapping_val):
            if isinstance(mapping_val, str):
                if mapping_val not in row.index:
                    if mapping_val not in self._missing_cols_warned:
                        logger.warning(
                            f"Column '{mapping_val}' not found in row. Mapping it to 'None'."
                        )
                        self._missing_cols_warned.add(mapping_val)
                return row.get(mapping_val)
            elif isinstance(mapping_val, dict):
                return {k: _get_value(v) for k, v in mapping_val.items()}
            elif isinstance(mapping_val, list):
                return [_get_value(v) for v in mapping_val]
            else:
                return mapping_val

        return _get_value(self.mapping)

    def _process_row(self, index: int, row: pd.Series) -> Dict[str, Any]:
        """Processes a single row: calls API and handles exceptions."""
        result = {"index": index, "response": None, "exception_summary": None}
        try:
            payload = self._prepare_payload(row)
            url = self.api_url
            if self.method == "GET":
                # For GET, we support URL templating using mapping values.
                # If the URL contains placeholders like {lat}, we fill them.
                # Remaining mapping fields are passed as query parameters.
                params = payload.copy()
                try:
                    # Look for placeholders in the URL
                    placeholders = re.findall(r"\{([^{}]+)\}", self.api_url)
                    if placeholders:
                        # Create a dict for formatting and remove those keys from params
                        format_dict = {}
                        for p in placeholders:
                            if p in params:
                                format_dict[p] = params.pop(p)
                        url = self.api_url.format(**format_dict)
                    else:
                        # No placeholders, use everything as query params
                        pass
                except (KeyError, ValueError):
                    # If formatting fails, fallback to using all payload as query params
                    url = self.api_url
                    params = payload

                # If params is empty, set it to None for a cleaner request
                if not params:
                    params = None

                response = requests.get(
                    url,
                    params=params,
                    timeout=10,
                    auth=self.auth,
                    headers=self.headers,
                )
            else:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=10,
                    auth=self.auth,
                    headers=self.headers,
                )
            response.raise_for_status()
            json_response = response.json()

            # If the response is a dictionary and contains a 'data' key, extract it
            # This follows the common API pattern where the actual object is in 'data'
            if isinstance(json_response, dict) and "data" in json_response:
                result["response"] = json_response["data"]
            else:
                result["response"] = json_response
        except Exception as e:
            logger.error(f"Error processing row {index}: {str(e)}")
            result["exception_summary"] = str(e)
        return result

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Asynchronously processes each row of the DataFrame."""
        self._missing_cols_warned = set()
        return super().process_dataframe(df)


def read_tabular_file(file_path: str) -> pd.DataFrame:
    """Reads a tabular file (CSV, Excel, etc.) based on its extension, ensuring all data is read as strings."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, dtype=str)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path, dtype=str)
    elif ext == ".tsv":
        return pd.read_csv(file_path, sep="\t", dtype=str)
    elif ext == ".txt":
        # Let Pandas infer the delimiters by setting sep=None and using the python engine.
        return pd.read_csv(file_path, sep=None, engine="python", dtype=str)
    elif ext == ".parquet":
        return pd.read_parquet(file_path).astype(str)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def save_tabular_file(df: pd.DataFrame, original_path: str, suffix: str = "_enhanced"):
    """Saves the DataFrame to the same format as the original file."""
    base, ext = os.path.splitext(original_path)
    output_path = f"{base}{suffix}{ext}"

    if ext == ".csv":
        df.to_csv(output_path, index=False)
    elif ext in [".xlsx", ".xls"]:
        df.to_excel(output_path, index=False)
    elif ext == ".tsv":
        df.to_csv(output_path, sep="\t", index=False)
    elif ext == ".txt":
        # For saving .txt, default to tab-separated (similar to .tsv)
        df.to_csv(output_path, sep="\t", index=False)
    elif ext == ".parquet":
        df.to_parquet(output_path, index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    logger.info(f"Enhanced file saved to: {output_path}")
    return output_path
