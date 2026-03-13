import concurrent.futures
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Union

import pandas as pd
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Verbatim:
    """Wrapper to indicate a value should be treated verbatim in mapping."""

    def __init__(self, value: Any):
        self.value = value


def verbatim(value: Any) -> Verbatim:
    """Helper to wrap a value as Verbatim for mapping."""
    return Verbatim(value)


class BaseEnhancer:
    """Base class for enhancing DataFrames asynchronously."""

    def __init__(
        self,
        max_workers: int = 5,
        flatten_response: bool = True,
        flatten_prefix: str = None,
        response_column_name: str = "response",
    ):
        self.max_workers = max_workers
        self.flatten_response = flatten_response
        self.flatten_prefix = flatten_prefix
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
            if self.flatten_prefix:
                res_df = res_df.add_prefix(self.flatten_prefix)
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
        api_url: str = None,
        mapping: Dict[str, Any] = None,
        file_path: Union[str, Path] = None,
        max_workers: int = 5,
        auth: Any = None,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        cert: Any = None,
        method: str = "POST",
        post_as_json: bool = True,
        post_json_as_string: bool = False,
        flatten_response: bool = True,
        flatten_prefix: str = None,
        response_column_name: str = "api_response",
    ):
        """
        :param api_url: The URL of the API to call.
                        Can contain placeholders for GET requests.
        :param mapping: Dictionary mapping API field names to DataFrame column names.
                        Example: {'user_id': 'id', 'user_name': 'name'}
        :param file_path: Path to the tabular file to process.
        :param max_workers: Number of threads for parallel processing.
        :param auth: Optional authentication for the API call
                     (e.g., requests.auth.HTTPBasicAuth).
        :param headers: Optional custom headers for the API call
                        (e.g., for API Key or Bearer Token).
        :param params: Optional constant query parameters for all API calls.
        :param cert: Optional SSL certificate for the API call
                     (e.g., path to cert file or ('cert', 'key') tuple).
        :param method: HTTP method to use (POST or GET).
        :param post_as_json: Whether to send the POST payload as a JSON body 
                             (using the 'json' parameter) or as form data 
                             (using the 'data' parameter) (default: True).
        :param post_json_as_string: Whether to send the JSON payload as a 
                                    string in the 'data' parameter (default: False).
        :param flatten_response: Whether to expand the response into
                                 individual columns (default: True).
        :param flatten_prefix: Optional prefix to add to all flattened field names.
        :param response_column_name: Name of the response column when flattening
                                     is disabled (default: 'api_response').
        """
        super().__init__(
            max_workers=max_workers,
            flatten_response=flatten_response,
            flatten_prefix=flatten_prefix,
            response_column_name=response_column_name,
        )
        self.api_url = api_url
        self.mapping = mapping
        self.auth = auth
        self.headers = headers
        self.params = params
        self.cert = cert
        self.method = method.upper() if method else "POST"
        self.post_as_json = post_as_json
        self.post_json_as_string = post_json_as_string
        self.file_path = str(file_path) if file_path else None
        self.sep = None
        self.df = None
        self._missing_cols_warned = set()

    def read(self) -> pd.DataFrame:
        """
        Reads the tabular file and detects formatting (e.g., delimiter).
        """
        if self.file_path is None:
            raise ValueError("No file path provided.")

        ext = os.path.splitext(self.file_path)[1].lower()
        if ext in [".csv", ".tsv", ".txt"]:
            # Try to detect the delimiter for text files
            import csv

            with open(self.file_path, "r", encoding="utf-8") as f:
                sample = f.read(2048)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    self.sep = dialect.delimiter
                except Exception:
                    # Fallback to defaults if sniffing fails
                    if ext == ".tsv":
                        self.sep = "\t"
                    else:
                        self.sep = ","

            self.df = pd.read_csv(self.file_path, sep=self.sep, dtype=str)
        elif ext in [".xlsx", ".xls"]:
            self.df = pd.read_excel(self.file_path, dtype=str)
        elif ext == ".parquet":
            self.df = pd.read_parquet(self.file_path).astype(str)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        return self.df

    def enhance(self) -> pd.DataFrame:
        """
        Enhances the loaded DataFrame using the configured API.
        """
        if self.df is None:
            raise ValueError("No data loaded. Call read() first.")

        if self.api_url is None or self.mapping is None:
            raise ValueError("API URL and mapping must be configured.")

        self.df = self.process_dataframe(self.df)
        return self.df

    def save(self, suffix: str = "_enhanced") -> str:
        """Saves the DataFrame to the same format as the original file.

        :param suffix: Suffix to append to the output filename.
        """
        if self.df is None:
            raise ValueError("No data to save. Call read() and enhance() first.")

        if self.file_path is None:
            raise ValueError("No file path provided for saving.")

        base, ext = os.path.splitext(self.file_path)
        output_path = f"{base}{suffix}{ext}"

        # Default parameters for save methods
        kwargs = {"index": False}
        if self.sep:
            kwargs["sep"] = self.sep

        # Map extensions to their save methods and parameters
        if ext == ".csv":
            method = self.df.to_csv
        elif ext in [".xlsx", ".xls"]:
            method = self.df.to_excel
        elif ext == ".tsv":
            method = self.df.to_csv
            if "sep" not in kwargs:
                kwargs["sep"] = "\t"
        elif ext == ".txt":
            method = self.df.to_csv
            if "sep" not in kwargs:
                kwargs["sep"] = ","
        elif ext == ".parquet":
            method = self.df.to_parquet
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        method(output_path, **kwargs)

        logger.info(f"Enhanced file saved to: {output_path}")
        return output_path

    def _prepare_payload(self, row: pd.Series) -> Dict[str, Any]:
        """Constructs the JSON payload from the row based on mapping."""

        def _get_value(mapping_val):
            if isinstance(mapping_val, Verbatim):
                return mapping_val.value
            elif isinstance(mapping_val, str):
                if mapping_val not in row.index:
                    if mapping_val not in self._missing_cols_warned:
                        logger.warning(
                            f"Column '{mapping_val}' not found in row. "
                            "Mapping it to 'None'."
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

                # Merge with global params if provided
                if self.params:
                    if params is None:
                        params = self.params.copy()
                    else:
                        params.update(self.params)

                response = requests.get(
                    url,
                    params=params,
                    timeout=10,
                    auth=self.auth,
                    headers=self.headers,
                    cert=self.cert,
                )
            else:
                headers = self.headers.copy() if self.headers else {}
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"

                if self.post_as_json:
                    response = requests.post(
                        url,
                        json=payload,
                        params=self.params,
                        timeout=10,
                        auth=self.auth,
                        headers=headers,
                        cert=self.cert,
                    )
                else:
                    if self.post_json_as_string:
                        payload = json.dumps(payload)

                    response = requests.post(
                        url,
                        data=payload,
                        params=self.params,
                        timeout=10,
                        auth=self.auth,
                        headers=headers,
                        cert=self.cert,
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
