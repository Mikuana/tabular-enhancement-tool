# Tabular-Enhancement-Tool

[![Documentation Status](https://readthedocs.org/projects/tabular-enhancement-tool/badge/?version=latest)](https://tabular-enhancement-tool.readthedocs.io/en/latest/?badge=latest)
[![Python Tests](https://github.com/Junie/Tabular-Enhancement-Tool/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Junie/Tabular-Enhancement-Tool/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/Junie/Tabular-Enhancement-Tool/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/Junie/Tabular-Enhancement-Tool)

A Python package for asynchronously enhancing tabular files (CSV, Excel, TSV, TXT) by calling external APIs for each row.

## Why Tabular-Enhancement-Tool?

In modern data lake architectures, raw tabular data (e.g., event logs, daily exports, customer records) often arrives in formats like CSV, Excel, or TSV. To make this data actionable, it frequently needs to be enriched with information residing in other systems—such as CRM details, geolocation data, or legacy internal services—accessible only via REST APIs.

The **Tabular-Enhancement-Tool (tet)** is designed to streamline this enrichment process:

- **Seamless Data Lake Integration**: Easily process incoming files by mapping existing columns to API requests.
- **High Performance via Multi-threading**: Instead of sequential processing, which can take hours for large files, this tool utilizes a thread pool to handle hundreds of rows concurrently.
- **Data Integrity and Precision**: The tool instructs Pandas to treat all inputs as strings, ensuring that original data—like ZIP codes with leading zeros or numeric IDs—is **retained exactly** as it appeared in the source.
- **Append-Only Enhancement**: Your original columns are never modified. The API's responses are appended as new columns (`api_response` and `exception_summary`), allowing you to preserve the lineage of the raw data while adding new value.
- **Strict Order Preservation**: Even with parallel execution, the output rows are guaranteed to match the order of the input file, making it safe for downstream processes that rely on stable indexing.

## Features

- **Multi-threaded processing**: Processes rows in parallel using `ThreadPoolExecutor` for high performance.
- **Asynchronous API calls**: Fetches data from external JSON-based APIs asynchronously.
- **Order preservation**: Ensures the output file matches the original row order, even with concurrent processing.
- **Flexible field mapping**: Map DataFrame columns to API payload fields via a simple dictionary/JSON.
- **REST API Authentication**: Supports Basic Auth, Bearer Token, and API Key authentication schemes.
- **Robust error handling**: Captures API errors and exceptions into a dedicated `exception_summary` column for easy debugging.
- **Multi-format support**: Handles CSV, TSV, TXT, and Excel (`.xlsx`, `.xls`) files out of the box.

## Installation

You can install the package directly from the source directory:

```bash
pip install .
```

This will automatically install the required dependencies (`pandas`, `requests`, `openpyxl`) and provide the `tabular-enhancer` command.

## Usage

### Command Line Interface (CLI)

After installation, you can run the tool using the `tabular-enhancer` command:

```bash
tabular-enhancer input_data.csv \
    --api_url "https://api.example.com/process" \
    --mapping '{"api_field_1": "csv_column_a", "api_field_2": "csv_column_b"}' \
    --max_workers 10
```

**Arguments:**
- `input_file`: Path to your CSV, Excel, TSV, or TXT file.
- `--api_url`: The endpoint where the POST request will be sent.
- `--mapping`: A JSON string mapping API payload keys to your file's column names.
- `--max_workers`: (Optional) Number of concurrent threads (default: 5).
- `--auth_type`: (Optional) Authentication type (`basic`, `bearer`, or `apikey`).
- `--auth_user`: (Optional) Username for `basic` auth.
- `--auth_pass`: (Optional) Password for `basic` auth.
- `--auth_token`: (Optional) Token for `bearer` or `apikey` auth.
- `--auth_header`: (Optional) Custom header for `apikey` auth (default: `X-API-Key`).

**CLI Authentication Examples:**

```bash
# Basic Auth
tabular-enhancer data.csv --api_url "..." --mapping '...' --auth_type basic --auth_user "admin" --auth_pass "secret"

# Bearer Token
tabular-enhancer data.csv --api_url "..." --mapping '...' --auth_type bearer --auth_token "your_token"

# API Key
tabular-enhancer data.csv --api_url "..." --mapping '...' --auth_type apikey --auth_token "your_api_key"
```

### Python Library Usage

You can also integrate `tabular_enhancement_tool` into your own Python scripts.

```python
import pandas as pd
import tabular_enhancement_tool as tet

# 1. Load your data
df = tet.read_tabular_file("my_data.xlsx")

# 2. Configure the enhancer
api_url = "https://api.example.com/v1/enrich"
mapping = {
    "user_id": "ID",
    "user_name": "Full Name"
}

# 2.1 Basic Auth (Optional)
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth("username", "password")

# 2.2 Bearer Token (Optional)
# headers = {"Authorization": "Bearer YOUR_TOKEN"}

enhancer = tet.TabularEnhancer(api_url, mapping, max_workers=5, auth=auth)

# 3. Process the DataFrame
df_enhanced = enhancer.process_dataframe(df)

# 4. Save the results
# This will save to my_data_enhanced.xlsx
tet.save_tabular_file(df_enhanced, "my_data.xlsx")
```

## Data Output

The output file will contain all original columns plus two new columns:
1. `api_response`: The JSON response from the API for that row.
2. `exception_summary`: Any error message encountered during the API call (e.g., timeouts, 404, 500). If no error occurred, this field will be null.

## Running Tests

The project uses `pytest` for testing. You can run all tests using the following command:

```bash
pytest
```

If you prefer `unittest`, it is still compatible:

```bash
python -m unittest discover tests
```
