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
- ``--mapping``: (Required) A JSON string mapping API payload keys to your file's column names. Supports nested objects and lists. e.g. ``'{"personId": "id", "address": [{"street": "st"}]}'``.
- ``--method``: (Optional) HTTP method to use (``POST`` or ``GET``, default: ``POST``).
- ``--auth_type``: (Optional) Authentication type (``basic``, ``bearer``, or ``apikey``).
- ``--auth_user``: (Optional) Username for ``basic`` auth.
- ``--auth_pass``: (Optional) Password for ``basic`` auth.
- ``--auth_token``: (Optional) Token for ``bearer`` or ``apikey`` auth.
- ``--auth_header``: (Optional) Custom header for ``apikey`` auth (default: ``X-API-Key``).
- ``--params``: (Optional) JSON string of constant query parameters for all API calls.
- ``--cert``: (Optional) Path to SSL certificate file (.pem) or JSON array of ('cert', 'key') tuple.

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

   # Custom Parameters and SSL Certificate
   tet data.csv --api_url "..." --mapping '...' --params '{"version": "v1"}' --cert "/path/to/cert.pem"

   # GET request with URL templating
   tet data.csv --api_url "https://api.weather.gov/points/{lat},{lon}" --mapping '{"lat": "latitude", "lon": "longitude"}' --method GET

Python API
----------

The `Tabular-Enhancement-Tool` provides a flexible Python API for integrating enhancement logic directly into your data pipelines. The core of the library is the ``TabularEnhancer`` class which handles the entire lifecycle of data enhancement, from reading the source file to saving the results.

Core Concepts
~~~~~~~~~~~~~

The ``TabularEnhancer`` class follows a simple workflow:
1.  **Initialization**: Configure the source file path and API enhancement settings.
2.  **Reading**: Call ``read()`` to load the data and automatically detect the file format and delimiter.
3.  **Enhancement**: Call ``enhance()`` to asynchronously process each row through the configured API.
4.  **Saving**: Call ``save()`` to write the enhanced data back to a new file in the original format.

REST API Enhancement
~~~~~~~~~~~~~~~~~~~~

The ``TabularEnhancer`` class is used to enrich data from any REST API that accepts and returns JSON.

.. code-block:: python

   import tabular_enhancement_tool as tet

   # API and File Configuration
   file_path = "my_data.csv"
   api_url = "https://api.example.com/v1/enrich"
   mapping = {"user_id": "ID", "dept": "Department"}
   
   # Create the enhancer
   enhancer = tet.TabularEnhancer(
       file_path=file_path,
       api_url=api_url, 
       mapping=mapping,
       method="POST",
       max_workers=10
   )

   # Full workflow
   enhancer.read()
   enhancer.enhance()
   enhancer.save(suffix="_enhanced")

**TabularEnhancer Parameters:**

*   ``file_path`` (str or Path, optional): Path to the tabular file to process. Required if using ``read()`` or ``save()``.
*   ``api_url`` (str, optional): The base URL of the REST API. For ``GET`` requests, you can use curly braces for URL templating (e.g., ``https://api.com/user/{id}``). Required if using ``enhance()``.
*   ``mapping`` (dict, optional): A dictionary where keys are the field names expected by the API, and values are the column names in your DataFrame. Supports nested dictionaries and lists for complex payloads. Required if using ``enhance()``.
*   ``method`` (str, optional): The HTTP method to use (``"POST"`` or ``"GET"``). Defaults to ``"POST"``.
*   ``max_workers`` (int, optional): The number of concurrent threads to use. Defaults to ``5``.
*   ``auth`` (Any, optional): Authentication object (e.g., ``requests.auth.HTTPBasicAuth("user", "pass")``).
*   ``headers`` (dict, optional): Custom headers for the request. Often used for Bearer Tokens: ``{"Authorization": "Bearer ..."}``.
*   ``params`` (dict, optional): Constant query parameters to be sent with every request. For ``GET`` requests, these are merged with mapping-derived parameters.
*   ``cert`` (str or tuple, optional): SSL certificate for the API call. Can be a path to a ``.pem`` file or a ``('cert', 'key')`` tuple.
*   ``flatten_response`` (bool, optional): If ``True`` (default), the JSON response keys are expanded into individual columns. If ``False``, the entire response is stored as a dictionary in a single column.
*   ``response_column_name`` (str, optional): The name of the column where the raw response is stored if ``flatten_response`` is ``False``.
