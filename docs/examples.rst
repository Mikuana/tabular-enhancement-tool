Examples
========

This page provides practical examples of how to use the `Tabular-Enhancement-Tool` for various data enrichment scenarios.

REST API Enhancement (POST)
---------------------------

This example demonstrates how to enrich a CSV file by sending its rows as JSON payloads to a REST POST endpoint using ``httpbin.org``.

.. code-block:: python

    import tabular_enhancement_tool as tet
    import os

    # 1. Read the tabular file
    # Ensure you have a 'posts_data.csv' with columns: title, body, userId
    df = tet.read_tabular_file("posts_data.csv")
    
    # 2. Configure the enhancer
    # The mapping defines which CSV columns map to the JSON payload fields
    api_url = "https://httpbin.org/post"
    mapping = {
        "title": "title",
        "body": "body",
        "userId": "userId"
    }
    
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        method="POST",
        max_workers=5
    )
    
    # 3. Process the DataFrame
    # Responses are automatically flattened into separate columns by default.
    df_enhanced = enhancer.process_dataframe(df)
    
    # 4. Save the results
    tet.save_tabular_file(df_enhanced, "posts_data.csv", suffix="_enhanced")

REST API Enhancement (GET with URL Templating)
----------------------------------------------

This example shows how to use GET requests with dynamic URL templating to fetch weather data from the National Weather Service (NWS).

.. code-block:: python

    import tabular_enhancement_tool as tet

    # 1. Read data with coordinates (columns: lat, lon)
    df = tet.read_tabular_file("cities_coords.csv")
    
    # 2. Configure the NWS API enhancer
    # The URL template uses {lat} and {lon} placeholders
    api_url = "https://api.weather.gov/points/{lat},{lon}"
    mapping = {
        "lat": "lat",
        "lon": "lon"
    }
    headers = {
        "User-Agent": "(myweatherapp.com, contact@example.com)"
    }
    
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        method="GET",
        headers=headers
    )
    
    # 3. Process the DataFrame
    # The NWS API 'data' field is automatically extracted and flattened.
    df_enhanced = enhancer.process_dataframe(df)
    
    # 4. Save the results
    tet.save_tabular_file(df_enhanced, "cities_coords.csv", suffix="_weather")

SQLAlchemy Database Enhancement
-------------------------------

Enrich your tabular data by performing lookups in a relational database using SQLAlchemy.

.. code-block:: python

    import tabular_enhancement_tool as tet

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
