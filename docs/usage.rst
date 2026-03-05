Usage
=====

Command Line Interface (CLI)
----------------------------

After installation, you can run the tool using the ``tet`` command:

.. code-block:: bash

   tet input_data.csv \
       --api_url "https://api.example.com/process" \
       --mapping '{"api_field_1": "csv_column_a", "api_field_2": "csv_column_b"}' \
       --max_workers 10

**Arguments:**

- ``input_file``: Path to your CSV, Excel, TSV, TXT, or Parquet file.
- ``--max_workers``: (Optional) Number of concurrent threads (default: 5).
- ``--no_flatten``: (Optional) Do not expand response objects into individual columns.

**API Options:**

- ``--api_url``: (Required) The endpoint where the request will be sent.
- ``--mapping``: (Required) A JSON string mapping API payload keys to your file's column names. e.g. ``'{"api_field": "csv_column"}'``.
- ``--method``: (Optional) HTTP method to use (``POST`` or ``GET``, default: ``POST``).
- ``--auth_type``: (Optional) Authentication type (``basic``, ``bearer``, or ``apikey``).
- ``--auth_user``: (Optional) Username for ``basic`` auth.
- ``--auth_pass``: (Optional) Password for ``basic`` auth.
- ``--auth_token``: (Optional) Token for ``bearer`` or ``apikey`` auth.
- ``--auth_header``: (Optional) Custom header for ``apikey`` auth (default: ``X-API-Key``).

CLI Usage Example
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # REST API Enhancement
   tet input.csv \
       --api_url "https://api.example.com/process" \
       --mapping '{"user_id": "id"}'

CLI Authentication Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Basic Auth
   tet data.csv --api_url "..." --mapping '...' --auth_type basic --auth_user "admin" --auth_pass "secret"

   # Bearer Token
   tet data.csv --api_url "..." --mapping '...' --auth_type bearer --auth_token "your_token"

   # API Key
   tet data.csv --api_url "..." --mapping '...' --auth_type apikey --auth_token "your_api_key"

   # GET request with URL templating
   tet data.csv --api_url "https://api.weather.gov/points/{lat},{lon}" --mapping '{"lat": "latitude", "lon": "longitude"}' --method GET

Python API
----------

The `Tabular-Enhancement-Tool` provides a flexible Python API for integrating enhancement logic directly into your data pipelines. The core of the library consists of "Enhancer" classes that handle the asynchronous processing of Pandas DataFrames.

Core Concepts
~~~~~~~~~~~~~

All enhancers follow a similar pattern:
1.  **Initialization**: Configure the source of enhancement (API) and the mapping between your local data and the remote fields.
2.  **Processing**: Call ``process_dataframe(df)`` to start the asynchronous enrichment. This method returns a new DataFrame with the original data plus the new columns.
3.  **Data Preservation**: All original columns are preserved. New data is appended, and an ``exception_summary`` column is added to help identify any rows that failed to process.

REST API Enhancement
~~~~~~~~~~~~~~~~~~~~

The ``TabularEnhancer`` class is used to enrich data from any REST API that accepts and returns JSON.

.. code-block:: python

   import tabular_enhancement_tool as tet

   # Load data
   df = tet.read_tabular_file("my_data.xlsx")

   # API Configuration
   api_url = "https://api.example.com/v1/enrich"
   mapping = {"user_id": "ID", "dept": "Department"}
   
   # Create the enhancer
   enhancer = tet.TabularEnhancer(
       api_url=api_url, 
       mapping=mapping,
       method="POST",
       max_workers=10
   )

   # Process the DataFrame
   df_enhanced = enhancer.process_dataframe(df)

   # Save the result
   tet.save_tabular_file(df_enhanced, "my_data.xlsx", suffix="_enhanced")

**TabularEnhancer Parameters:**

*   ``api_url`` (str): The base URL of the REST API. For ``GET`` requests, you can use curly braces for URL templating (e.g., ``https://api.com/user/{id}``).
*   ``mapping`` (dict): A dictionary where keys are the field names expected by the API, and values are the column names in your DataFrame.
*   ``method`` (str, optional): The HTTP method to use (``"POST"`` or ``"GET"``). Defaults to ``"POST"``.
*   ``max_workers`` (int, optional): The number of concurrent threads to use. Defaults to ``5``.
*   ``auth`` (Any, optional): Authentication object (e.g., ``requests.auth.HTTPBasicAuth("user", "pass")``).
*   ``headers`` (dict, optional): Custom headers for the request. Often used for Bearer Tokens: ``{"Authorization": "Bearer ..."}``.
*   ``flatten_response`` (bool, optional): If ``True`` (default), the JSON response keys are expanded into individual columns. If ``False``, the entire response is stored as a dictionary in a single column.
*   ``response_column_name`` (str, optional): The name of the column where the raw response is stored if ``flatten_response`` is ``False``.


Utility Functions
~~~~~~~~~~~~~~~~~

The tool includes helper functions to ensure data types are handled correctly (reading all columns as strings to prevent data loss).

*   ``read_tabular_file(file_path)``: Reads CSV, Excel, TSV, TXT, or Parquet files, ensuring all data is imported as strings.
*   ``save_tabular_file(df, original_path, suffix="_enhanced")``: Saves a DataFrame to the same format as the source file, appending a suffix to the filename.
