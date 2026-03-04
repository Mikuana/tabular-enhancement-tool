# Tabular-Enhancement-Tool

[![Documentation Status](https://readthedocs.org/projects/tabular-enhancement-tool/badge/?version=latest)](https://tabular-enhancement-tool.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/Tabular-Enhancement-Tool.svg)](https://badge.fury.io/py/Tabular-Enhancement-Tool)
[![Python Tests](https://github.com/Junie/Tabular-Enhancement-Tool/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Junie/Tabular-Enhancement-Tool/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/Junie/Tabular-Enhancement-Tool/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/Junie/Tabular-Enhancement-Tool)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python package for asynchronously enhancing tabular files (CSV, Excel, TSV, TXT) by calling external APIs for each row.

## Why Tabular-Enhancement-Tool?

In modern data lake architectures, raw tabular data (e.g., event logs, daily exports, customer records) often arrives in formats like CSV, Excel, or TSV. To make this data actionable, it frequently needs to be enriched with information residing in other systems—such as CRM details, geolocation data, or legacy internal services—accessible only via REST APIs.

The **Tabular-Enhancement-Tool (tet)** is designed to streamline this enrichment process:

- **Multi-source enhancement**: Fetches data from external JSON-based REST APIs or SQLAlchemy-compatible databases.
- **High Performance via Multi-threading**: Instead of sequential processing, which can take hours for large files, this tool utilizes a thread pool to handle hundreds of rows concurrently.
- **Data Integrity and Precision**: The tool instructs Pandas to treat all inputs as strings, ensuring that original data—like ZIP codes with leading zeros or numeric IDs—is **retained exactly** as it appeared in the source.
- **Append-Only Enhancement**: Your original columns are never modified. The responses are appended as new columns (`api_response` or `odbc_response`, and `exception_summary`), allowing you to preserve the lineage of the raw data while adding new value.
- **Strict Order Preservation**: Even with parallel execution, the output rows are guaranteed to match the order of the input file, making it safe for downstream processes that rely on stable indexing.
- **Flexible field mapping**: Map DataFrame columns to API payload fields or database query filters.
- **REST API Authentication**: Supports Basic Auth, Bearer Token, and API Key authentication schemes.
- **SQLAlchemy Integration**: Supports any database with a SQLAlchemy dialect (PostgreSQL, MySQL, SQLite, Oracle, SQL Server, etc.).

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
- `--max_workers`: (Optional) Number of concurrent threads (default: 5).

**API Options:**
- `--api_url`: The endpoint where the POST request will be sent.
- `--mapping`: A JSON string mapping API payload keys to your file's column names. e.g. `'{"api_field": "csv_column"}'`.
- `--auth_type`: (Optional) Authentication type (`basic`, `bearer`, or `apikey`).
- `--auth_user`: (Optional) Username for `basic` auth.
- `--auth_pass`: (Optional) Password for `basic` auth.
- `--auth_token`: (Optional) Token for `bearer` or `apikey` auth.
- `--auth_header`: (Optional) Custom header for `apikey` auth (default: `X-API-Key`).

**SQLAlchemy Options:**
- `--db_url`: The SQLAlchemy connection URL to the target database.
- `--table_name`: Name of the table to query for enhancement.
- `--mapping`: A JSON list of column names in your file to be used as filters (WHERE clause) for the query. e.g. `'["email_address"]'`.

**CLI Usage Examples:**

```bash
# REST API Enhancement
tabular-enhancer input.csv \
    --api_url "https://api.example.com/process" \
    --mapping '{"user_id": "id"}'

# SQLAlchemy Database Enhancement
tabular-enhancer data.xlsx \
    --db_url "postgresql://user:pass@localhost/dbname" \
    --table_name "users" \
    --mapping '["email_address"]'
```

**CLI Authentication Examples:**

```bash
# Basic Auth
tabular-enhancer data.csv --api_url "..." --mapping '...' --auth_type basic --auth_user "admin" --auth_pass "secret"

# Bearer Token
tabular-enhancer data.csv --api_url "..." --mapping '...' --auth_type bearer --auth_token "your_token"

# API Key
tabular-enhancer data.csv --api_url "..." --mapping '...' --auth_type apikey --auth_token "your_api_key"
```

### REST API Enhancement

```python
import pandas as pd
import tabular_enhancement_tool as tet

# Load data
df = tet.read_tabular_file("my_data.xlsx")

# API Configuration
api_url = "https://api.example.com/v1/enrich"
mapping = {"user_id": "ID"}
enhancer = tet.TabularEnhancer(api_url, mapping)

# Process
df_enhanced = enhancer.process_dataframe(df)

# Save
tet.save_tabular_file(df_enhanced, "my_data.xlsx")
```

### SQLAlchemy Database Enhancement (Core)

```python
import pandas as pd
import tabular_enhancement_tool as tet

# Load data
df = tet.read_tabular_file("data.csv")

# SQLAlchemy Configuration
db_url = "postgresql://user:pass@localhost/dbname"
mapping = ["ID"]
enhancer = tet.ODBCEnhancer(db_url, mapping, table_name="orders")

# Process
df_enhanced = enhancer.process_dataframe(df)

# Save
tet.save_tabular_file(df_enhanced, "data.csv")
```

### SQLAlchemy Database Enhancement (ORM)

```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String
import tabular_enhancement_tool as tet

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)

# Load data
df = tet.read_tabular_file("data.csv")

# Process using ORM model
enhancer = tet.ODBCEnhancer("sqlite:///mydb.db", mapping=["id"], model=User)
df_enhanced = enhancer.process_dataframe(df)
```

## Data Output

The output file will contain all original columns exactly as they appeared in the source, plus additional columns based on the enhancement method used.

### REST API Method
When using `TabularEnhancer`, the following columns are appended:
1. `api_response`: The full JSON response from the API for that row, stored as a dictionary/JSON-formatted string.
2. `exception_summary`: If an error occurs (e.g., 404, 500, Timeout), the error message is captured here.

**Example:**
| id | name | api_response | exception_summary |
|----|------|--------------|-------------------|
| 01 | Alice| `{"status": "active", "tier": "gold"}` | |
| 02 | Bob  | | `500 Server Error` |

### SQLAlchemy Method
When using `ODBCEnhancer` (SQLAlchemy), the following columns are appended:
1. `odbc_response`: A dictionary representing the database row found, where keys are column names and values are the database values.
2. `exception_summary`: Captures any database-related errors (e.g., connection issues, invalid queries).

**Example:**
| user_id | email | odbc_response | exception_summary |
|---------|-------|---------------|-------------------|
| 101     | a@b.com| `{"id": 101, "role": "admin", "last_login": "2024-01-01"}` | |
| 102     | c@d.com| | `Table 'users' not found` |

## Running Tests

The project uses `pytest` for testing. You can run all tests using the following command:

```bash
pytest
```

If you prefer `unittest`, it is still compatible:

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Development and CI/CD

- **Testing**: Run `pytest` locally or check the "Python Tests" GitHub Action.
- **Documentation**: Managed by Sphinx and hosted on Read the Docs.
- **Publishing**: The `main` branch is automatically built and published to PyPI on every push. **Note**: Remember to bump the version in `setup.py` and `tabular_enhancement_tool/__init__.py` before pushing to `main`.

## Credits

This tool was authored by **Christopher Boyd** and co-authored/developed by **Junie**, an autonomous programmer developed by JetBrains.
