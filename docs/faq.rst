FAQ & Troubleshooting
====================

Frequently Asked Questions
--------------------------

**Q: Does the tool modify my input file?**
A: No. By default, the tool appends a suffix (e.g., ``_enhanced``) to the original filename and creates a new file. Your original data remains untouched.

**Q: Why are all my columns being read as strings?**
A: This is intentional. To prevent data loss (like leading zeros in ZIP codes or IDs), the tool reads all tabular data as strings. You can convert them back to the appropriate types in your own pipeline after enhancement.

**Q: Can I use this with large files?**
A: Yes. The tool uses a thread pool for asynchronous processing, which significantly improves performance compared to sequential row processing. However, keep in mind that performance also depends on the response time of the API or database you are calling.

**Q: What happens if an API call fails for a single row?**
A: The tool captures the error and records it in an ``exception_summary`` column for that row. The rest of the DataFrame will continue to be processed.

Troubleshooting
---------------

**Issue: "ModuleNotFoundError: No module named 'tabular_enhancement_tool'"**
*   **Solution**: Ensure you have installed the package using ``pip install .`` from the project root or ``pip install tabular-enhancement-tool``. If you are using a virtual environment, make sure it is activated.

**Issue: "Column '...' not found in row. Mapping it to 'None'."**
*   **Solution**: Check your mapping configuration. The column names provided in the mapping must match the column names in your input file (case-sensitive).

**Issue: API authentication is failing.**
*   **Solution**: Verify your credentials and authentication type. If you're using ``apikey``, check if the header name (default: ``X-API-Key``) is correct for your API.

**Issue: SQLAlchemy connection error.**
*   **Solution**: Ensure you have a valid SQLAlchemy connection URL and that the necessary database drivers (like ``psycopg2`` for PostgreSQL) are installed. The tool includes ``sqlalchemy``, but some drivers may need to be installed separately.
