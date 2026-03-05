Changelog
=========

All notable changes to the **Tabular-Enhancement-Tool** will be documented in this file.

v0.2.1 (2026-03-05)
-------------------

*   Added support for nested dictionaries and lists in API mapping for both POST and GET methods.
*   Updated documentation and README with nested mapping examples.
*   Achieved 100% test coverage for the core module.

v0.2.0 (2026-03-05)
-------------------

*   Removed ODBC/SQLAlchemy-based enhancement method.
*   Focused the package exclusively on REST-based POST and GET methods.
*   Updated documentation and CLI to remove all database-related references.
*   Removed `sqlalchemy` dependency from `setup.py`.

v0.1.5 (2026-03-04)
-------------------

*   Internal development and maintenance.

v0.1.4 (2026-03-04)
-------------------

*   Added detailed "Contributing", "Changelog", and "FAQ" pages to the documentation.
*   Improved documentation structure and content for better user guidance.

v0.1.3 (2026-03-04)
-------------------

*   Enhanced documentation with more narrative and explanation of classes and parameters.
*   Added comprehensive documentation for `TabularEnhancer`, `ODBCEnhancer`, and utility functions.

v0.1.2 (2026-03-04)
-------------------

*   Integrated MyST-Parser to use `README.md` as the main Sphinx documentation index page.
*   Updated documentation requirements to include `myst-parser`.

v0.1.1 (2026-03-04)
-------------------

*   Added initial Sphinx documentation including landing page, usage, and examples.
*   Added support for installation instructions via PyPI.

v0.1.0 (2026-03-04)
-------------------

*   Initial release of the **Tabular-Enhancement-Tool**.
*   Core functionality for REST API and SQLAlchemy database enhancement.
*   Support for CSV, Excel, TSV, TXT, and Parquet file formats.
*   High-performance asynchronous processing using thread pools.
*   Data type preservation by reading all inputs as strings.
*   Response flattening and append-only enhancement.
*   Flexible field mapping and various authentication schemes.
