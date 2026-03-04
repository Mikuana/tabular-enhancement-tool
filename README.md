# Tabular-Enhancement-Tool

[![Documentation Status](https://readthedocs.org/projects/tabular-enhancement-tool/badge/?version=latest)](https://tabular-enhancement-tool.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/Tabular-Enhancement-Tool.svg)](https://badge.fury.io/py/Tabular-Enhancement-Tool)
[![codecov](https://codecov.io/gh/Mikuana/tabular-enhancement-tool/graph/badge.svg?token=7ISFGBQMKK)](https://codecov.io/gh/Mikuana/tabular-enhancement-tool)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python package for asynchronously enhancing tabular files (CSV, Excel, TSV, TXT, Parquet) by calling external APIs for each row.

## Why Tabular-Enhancement-Tool?

In modern data lake architectures, raw tabular data (e.g., event logs, daily exports, customer records) often arrives in formats like CSV, Excel, or TSV. To make this data actionable, it frequently needs to be enriched with information residing in other systems—such as CRM details, geolocation data, or legacy internal services—accessible only via REST APIs.

The **Tabular-Enhancement-Tool (tet)** is designed to streamline this enrichment process:

- **Multi-source enhancement**: Fetches data from external JSON-based REST APIs or SQLAlchemy-compatible databases.
- **High Performance via Multi-threading**: Instead of sequential processing, which can take hours for large files, this tool utilizes a thread pool to handle hundreds of rows concurrently.
- **Data Integrity and Precision**: The tool instructs Pandas to treat all inputs as strings, ensuring that original data—like ZIP codes with leading zeros or numeric IDs—is **retained exactly** as it appeared in the source.
- **Append-Only Enhancement**: Your original columns are never modified. The responses are appended as new columns, allowing you to preserve the lineage of the raw data while adding new value.
- **Response Flattening**: By default, the tool expands API/Database response objects into individual columns, making the data immediately available for analysis. For REST APIs, the tool automatically extracts the `data` field from the JSON response if present, focusing on the core payload. This behavior can be disabled if a single nested object is preferred.
- **Strict Order Preservation**: Even with parallel execution, the output rows are guaranteed to match the order of the input file, making it safe for downstream processes that rely on stable indexing.
- **Flexible field mapping**: Map DataFrame columns to API payload fields or database query filters.
- **HTTP GET and POST support**: Choose the appropriate method for your API, with support for URL templating and query parameters.
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
- `input_file`: Path to your CSV, Excel, TSV, TXT, or Parquet file.
- `--max_workers`: (Optional) Number of concurrent threads (default: 5).
- `--no_flatten`: (Optional) Do not expand response objects into individual columns.

**API Options:**
- `--api_url`: The endpoint where the POST request will be sent.
- `--mapping`: A JSON string mapping API payload keys to your file's column names. e.g. `'{"api_field": "csv_column"}'`.
- `--method`: (Optional) HTTP method to use (`POST` or `GET`, default: `POST`).
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

# GET request with URL templating
tabular-enhancer data.csv --api_url "https://api.weather.gov/points/{lat},{lon}" --mapping '{"lat": "latitude", "lon": "longitude"}' --method GET
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

### REST API Enhancement (POST Example)

The following example demonstrates how to use the `httpbin.org` public API to simulate posting data from a CSV file.

```python
import tabular_enhancement_tool as tet

# Load data
df = tet.read_tabular_file("examples/posts_data.csv")

# HTTPBin API configuration
api_url = "https://httpbin.org/post"
mapping = {
    "title": "title",
    "body": "body",
    "userId": "userId"
}

enhancer = tet.TabularEnhancer(api_url, mapping, method="POST")

# Process
df_enhanced = enhancer.process_dataframe(df)

# Save
tet.save_tabular_file(df_enhanced, "examples/posts_data.csv", suffix="_enhanced")
```

### REST API Enhancement (GET with URL Templating)

```python
import tabular_enhancement_tool as tet

# Load data with coordinates
df = tet.read_tabular_file("cities.csv")

# NWS API example
api_url = "https://api.weather.gov/points/{lat},{lon}"
mapping = {"lat": "lat", "lon": "lon"}
headers = {"User-Agent": "(myweatherapp.com, contact@example.com)"}

enhancer = tet.TabularEnhancer(api_url, mapping, method="GET", headers=headers)

# Process
df_enhanced = enhancer.process_dataframe(df)
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

### SQLAlchemy Database Enhancement (SQLite Example)

This example shows how to use the `ODBCEnhancer` with a SQLite database to enrich a CSV file.

```python
import tabular_enhancement_tool as tet

# Load data
df = tet.read_tabular_file("users.csv")

# SQLite connection URL
db_url = "sqlite:///company_data.db"

# Match by 'email' and fetch related columns from the 'employees' table
enhancer = tet.ODBCEnhancer(
    connection_url=db_url,
    mapping=["email"],
    table_name="employees"
)

# Process and save
df_enhanced = enhancer.process_dataframe(df)
tet.save_tabular_file(df_enhanced, "users.csv", suffix="_enriched")
```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Development and CI/CD

- **Linting & Formatting**: Ruff is used to maintain high code quality and consistent style.
- **Documentation**: Managed by Sphinx and hosted on [Read the Docs](https://tabular-enhancement-tool.readthedocs.io/en/latest/). For more detailed examples and API documentation, please visit the official documentation site.

## Credits

This tool was authored by **Christopher Boyd** and co-authored/developed by **Junie**, an autonomous programmer developed by JetBrains.
