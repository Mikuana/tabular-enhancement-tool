# Tabular-Enhancement-Tool

[![Documentation Status](https://readthedocs.org/projects/tabular-enhancement-tool/badge/?version=latest)](https://tabular-enhancement-tool.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/Tabular-Enhancement-Tool.svg)](https://badge.fury.io/py/Tabular-Enhancement-Tool)
[![codecov](https://codecov.io/gh/Mikuana/tabular-enhancement-tool/graph/badge.svg?token=7ISFGBQMKK)](https://codecov.io/gh/Mikuana/tabular-enhancement-tool)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

>**WARNING**: this project is still in its early stages, and the code is written primarily by an AI coding agent. Please use with caution.

A Python package for asynchronously enhancing tabular files (CSV, Excel, TSV, TXT, Parquet) by calling external APIs for each row.

## Why

In modern data lake architectures, raw tabular data (e.g., event logs, daily exports, customer records) often arrives in formats like CSV, Excel, or TSV. To make this data actionable, it frequently needs to be enriched with information residing in other systems—such as CRM details, geolocation data, or legacy internal services—accessible only via REST APIs.

The **Tabular Enhancement Tool (tet)** is designed to streamline this enrichment process:

- **Multi-source enhancement**: Fetches data from external JSON-based REST APIs.
- **High Performance via Multi-threading**: Instead of sequential processing, which can take hours for large files, this tool utilizes a thread pool to handle hundreds of rows concurrently.
- **Data Integrity and Precision**: The tool instructs Pandas to treat all inputs as strings, ensuring that original data—like ZIP codes with leading zeros or numeric IDs—is **retained exactly** as it appeared in the source.
- **Append-Only Enhancement**: Your original columns are never modified. The responses are appended as new columns, allowing you to preserve the lineage of the raw data while adding new value.
- **Response Flattening**: By default, the tool expands API response objects into individual columns, making the data immediately available for analysis. For REST APIs, the tool automatically extracts the `data` field from the JSON response if present, focusing on the core payload. This behavior can be disabled if a single nested object is preferred.
- **Strict Order Preservation**: Even with parallel execution, the output rows are guaranteed to match the order of the input file, making it safe for downstream processes that rely on stable indexing.
- **Flexible field mapping**: Map DataFrame columns to API payload fields. Supports nested dictionaries and lists for complex JSON payloads.
- **HTTP GET and POST support**: Choose the appropriate method for your API, with support for URL templating and query parameters.
- **REST API Authentication**: Supports Basic Auth, Bearer Token, and API Key authentication schemes.

## Installation

You can install the package directly from the source directory:

```bash
pip install tabular-enhancement-tool
```

This will automatically install the required dependencies (`pandas`, `requests`, `openpyxl`) and provide the `tet` command.

## Usage

Read the docs.   [![Documentation Status](https://readthedocs.org/projects/tabular-enhancement-tool/badge/?version=latest)](https://tabular-enhancement-tool.readthedocs.io/en/latest/?badge=latest)

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Development and CI/CD

- **Linting & Formatting**: Ruff is used to maintain high code quality and consistent style.
- **Documentation**: Managed by Sphinx and hosted on [Read the Docs](https://tabular-enhancement-tool.readthedocs.io/en/latest/). [![Documentation Status](https://readthedocs.org/projects/tabular-enhancement-tool/badge/?version=latest)](https://tabular-enhancement-tool.readthedocs.io/en/latest/?badge=latest)
- **Tested**: via pytest and CodeCov. [![codecov](https://codecov.io/gh/Mikuana/tabular-enhancement-tool/graph/badge.svg?token=7ISFGBQMKK)](https://codecov.io/gh/Mikuana/tabular-enhancement-tool)

## Credits

This tool was authored by **Christopher Boyd** and co-authored/developed by **Junie**, an autonomous programmer developed by JetBrains.
