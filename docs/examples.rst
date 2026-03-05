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

        # 2. HTTPBin API Example (POST)
        # This public API echoes back the data sent in the request.
        api_url = "https://httpbin.org/post"

        # The mapping defines which CSV columns map to the JSON payload fields
        mapping = {"title": "title", "body": "body", "userId": "userId"}

        # 3. Create the enhancer
        enhancer = tet.TabularEnhancer(
            file_path=input_file,
            api_url=api_url,
            mapping=mapping,
            method="POST",
            max_workers=5
        )

        # 4. Read the tabular file
        enhancer.read()

        # 5. Process the data
        # By default, responses are automatically flattened into separate columns.
        enhancer.enhance()

        # 6. Save the results
        enhancer.save(suffix="_enhanced")

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
        # 1. Configure the enhancer with a Bearer Token
        # Pass the token in the headers
        token = "your_secret_token_here"
        api_url = "https://httpbin.org/post"
        mapping = {"title": "title", "body": "body", "userId": "userId"}

        enhancer = tet.TabularEnhancer(
            file_path="posts_data.csv",
            api_url=api_url,
            mapping=mapping,
            method="POST",
            headers={"Authorization": f"Bearer {token}"},
            max_workers=5
        )

        # 2. Read, enhance and save
        enhancer.read()
        enhancer.enhance()
        enhancer.save(suffix="_auth")

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
        # 1. Configure the NWS API enhancer
        # The URL template uses {lat} and {lon} placeholders
        api_url = "https://api.weather.gov/points/{lat},{lon}"
        mapping = {"lat": "lat", "lon": "lon"}
        headers = {"User-Agent": "(myweatherapp.com, contact@example.com)"}

        enhancer = tet.TabularEnhancer(
            file_path="cities_coords.csv",
            api_url=api_url,
            mapping=mapping,
            method="GET",
            headers=headers,
            max_workers=5
        )

        # 2. Process the data
        # The NWS API 'data' field is automatically extracted and flattened.
        enhancer.read()
        enhancer.enhance()

        # 3. Save the results
        enhancer.save(suffix="_weather")

    if __name__ == "__main__":
        main()

By default, the tool flattens the response into individual columns. You can disable this behavior to keep the raw response in a single column (``api_response``).

.. code-block:: python

    # Disable flattening to keep the raw response dictionary in one column
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        flatten_response=False
    )
    df_non_flattened = enhancer.process_dataframe(df)
