Examples
========

This page provides practical examples of how to use the ``Tabular-Enhancement-Tool`` for various data enrichment scenarios.

REST API Enhancement (POST)
---------------------------

This example demonstrates how to enrich a CSV file by sending its rows as JSON payloads to a REST POST endpoint using ``httpbin.org``.

**Input Data (posts_data.csv)**

.. list-table::
   :header-rows: 1

   * - id
     - title
     - body
     - userId
   * - 1
     - Sample Title 1
     - Sample Body 1
     - 1
   * - 2
     - Sample Title 2
     - Sample Body 2
     - 1
   * - 3
     - Sample Title 3
     - Sample Body 3
     - 2
   * - 4
     - Sample Title 4
     - Sample Body 4
     - 2
   * - 5
     - Sample Title 5
     - Sample Body 5
     - 3

**Code Example (httpbin_post_example.py)**

.. code-block:: python

    import tabular_enhancement_tool as tet
    import os

    def main():
        # 1. Path to our sample data
        input_file = "posts_data.csv"

        # 2. Read the tabular file
        df = tet.read_tabular_file(input_file)

        # 3. HTTPBin API Example (POST)
        # This public API echoes back the data sent in the request.
        api_url = "https://httpbin.org/post"

        # The mapping defines which CSV columns map to the JSON payload fields
        mapping = {"title": "title", "body": "body", "userId": "userId"}

        enhancer = tet.TabularEnhancer(
            api_url=api_url, mapping=mapping, method="POST", max_workers=5
        )

        # 4. Process the DataFrame
        # By default, responses are automatically flattened into separate columns.
        df_enhanced = enhancer.process_dataframe(df)

        # 5. Save the results
        tet.save_tabular_file(df_enhanced, input_file, suffix="_enhanced")

    if __name__ == "__main__":
        main()

**Output Data (posts_data_enhanced.csv)**

.. list-table::
   :header-rows: 1

   * - id
     - title
     - body
     - userId
     - exception_summary
   * - 1
     - Sample Title 1
     - Sample Body 1
     - 1
     - 
   * - 2
     - Sample Title 2
     - Sample Body 2
     - 1
     - 
   * - 3
     - Sample Title 3
     - Sample Body 3
     - 2
     - 
   * - 4
     - Sample Title 4
     - Sample Body 4
     - 2
     - 
   * - 5
     - Sample Title 5
     - Sample Body 5
     - 3
     - 

REST API Enhancement (POST with Authentication)
-----------------------------------------------

This example demonstrates how to use a Bearer Token with a POST request.

**Code Example (httpbin_auth_post_example.py)**

.. code-block:: python

    import tabular_enhancement_tool as tet

    def main():
        # 1. Read the tabular file
        df = tet.read_tabular_file("posts_data.csv")

        # 2. Configure the enhancer with a Bearer Token
        # Pass the token in the headers
        token = "your_secret_token_here"
        api_url = "https://httpbin.org/post"
        mapping = {"title": "title", "body": "body", "userId": "userId"}

        enhancer = tet.TabularEnhancer(
            api_url=api_url,
            mapping=mapping,
            method="POST",
            headers={"Authorization": f"Bearer {token}"},
            max_workers=5
        )

        # 3. Process the DataFrame
        df_enhanced = enhancer.process_dataframe(df)

        # 4. Save results
        tet.save_tabular_file(df_enhanced, "posts_data.csv", suffix="_auth")

    if __name__ == "__main__":
        main()

REST API Enhancement (GET with URL Templating)
----------------------------------------------

This example shows how to use GET requests with dynamic URL templating to fetch weather data from the National Weather Service (NWS).

**Input Data (cities_coords.csv)**

.. list-table::
   :header-rows: 1

   * - city
     - lat
     - lon
   * - New York
     - 40.7128
     - -74.0060
   * - Los Angeles
     - 34.0522
     - -118.2437
   * - Chicago
     - 41.8781
     - -87.6298
   * - Houston
     - 29.7604
     - -95.3698
   * - Phoenix
     - 33.4484
     - -112.0740

**Code Example (nws_weather_example.py)**

.. code-block:: python

    import tabular_enhancement_tool as tet

    def main():
        # 1. Read data with coordinates (columns: lat, lon)
        df = tet.read_tabular_file("cities_coords.csv")

        # 2. Configure the NWS API enhancer
        # The URL template uses {lat} and {lon} placeholders
        api_url = "https://api.weather.gov/points/{lat},{lon}"
        mapping = {"lat": "lat", "lon": "lon"}
        headers = {"User-Agent": "(myweatherapp.com, contact@example.com)"}

        enhancer = tet.TabularEnhancer(
            api_url=api_url,
            mapping=mapping,
            method="GET",
            headers=headers,
            max_workers=5
        )

        # 3. Process the DataFrame
        # The NWS API 'data' field is automatically extracted and flattened.
        df_enhanced = enhancer.process_dataframe(df)

        # 4. Save the results
        tet.save_tabular_file(df_enhanced, "cities_coords.csv", suffix="_weather")

    if __name__ == "__main__":
        main()

SQLAlchemy Database Enhancement
-------------------------------

Enrich your tabular data by performing lookups in a relational database using SQLAlchemy.

**Input Data (users_to_enrich.csv)**

.. list-table::
   :header-rows: 1

   * - email
   * - alice@example.com
   * - bob@example.com
   * - charlie@example.com
   * - unknown@example.com

**Code Example (sqlite_odbc_example.py)**

.. code-block:: python

    import tabular_enhancement_tool as tet

    def main():
        # 1. Read the tabular file
        df = tet.read_tabular_file("users_to_enrich.csv")

        # 2. Configure the Database enhancer
        # We match rows by the 'email' column and fetch all columns from the 'users' table.
        db_url = "sqlite:///sample_data.db"
        table_name = "users"
        mapping = ["email"]

        enhancer = tet.ODBCEnhancer(
            connection_url=db_url,
            mapping=mapping,
            table_name=table_name,
            max_workers=5
        )

        # 3. Process the DataFrame
        # Database row fields are flattened into the main DataFrame.
        df_enhanced = enhancer.process_dataframe(df)

        # 4. Save the results
        tet.save_tabular_file(df_enhanced, "users_to_enrich.csv", suffix="_enriched")

    if __name__ == "__main__":
        main()

**Output Data (users_to_enrich_enriched.csv)**

.. list-table::
   :header-rows: 1

   * - email
     - full_name
     - department
     - exception_summary
   * - alice@example.com
     - Alice Smith
     - Engineering
     - 
   * - bob@example.com
     - Bob Jones
     - Marketing
     - 
   * - charlie@example.com
     - Charlie Brown
     - HR
     - 
   * - unknown@example.com
     - 
     - 
     - 

Response Flattening
-------------------

By default, the tool flattens the response into individual columns. You can disable this behavior to keep the raw response in a single column (``api_response`` or ``odbc_response``).

.. code-block:: python

    # Disable flattening to keep the raw response dictionary in one column
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        flatten_response=False
    )
    df_non_flattened = enhancer.process_dataframe(df)
