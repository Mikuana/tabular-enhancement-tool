import tabular_enhancement_tool as tet
import os

def main():
    # 1. Path to our sample data
    input_file = os.path.join(os.path.dirname(__file__), "cities_coords.csv")
    
    # 2. Read the tabular file
    print(f"Reading {input_file}...")
    df = tet.read_tabular_file(input_file)
    
    # 3. National Weather Service (NWS) API Example
    # The NWS API requires a User-Agent header (identifying your application).
    headers = {
        "User-Agent": "(myweatherapp.com, contact@example.com)"
    }
    
    # We'll use the 'points' endpoint which takes latitude and longitude.
    # URL template uses {lat} and {lon} which correspond to our CSV columns.
    api_url = "https://api.weather.gov/points/{lat},{lon}"
    
    # The mapping defines which CSV columns fill the URL placeholders (for GET)
    # or the JSON payload (for POST).
    mapping = {
        "lat": "lat",
        "lon": "lon"
    }
    
    print("Enhancing data via NWS API (GET requests with URL templating)...")
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        method="GET",
        headers=headers,
        max_workers=5
    )
    
    # 4. Process the DataFrame
    df_enhanced = enhancer.process_dataframe(df)
    
    # 5. Save the results
    output_path = tet.save_tabular_file(df_enhanced, input_file, suffix="_weather")
    print(f"Process complete. Results saved to: {output_path}")
    
    # Display a snippet of the results
    print("\nSample Output:")
    print(df_enhanced[["city", "api_response", "exception_summary"]].head())

if __name__ == "__main__":
    main()
