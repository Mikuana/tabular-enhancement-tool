import tabular_enhancement_tool as tet
import os

def main():
    # 1. Path to our sample data
    input_file = os.path.join(os.path.dirname(__file__), "posts_data.csv")
    
    # 2. Read the tabular file
    print(f"Reading {input_file}...")
    df = tet.read_tabular_file(input_file)
    
    # 3. HTTPBin API Example (POST)
    # This public API echoes back the data sent in the request.
    api_url = "https://httpbin.org/post"
    
    # The mapping defines which CSV columns map to the JSON payload fields
    mapping = {
        "title": "title",
        "body": "body",
        "userId": "userId"
    }
    
    print("Enhancing data via HTTPBin API (POST requests)...")
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        method="POST",
        max_workers=5
    )
    
    # 4. Process the DataFrame
    df_enhanced = enhancer.process_dataframe(df)
    
    # 5. Save the results
    output_path = tet.save_tabular_file(df_enhanced, input_file, suffix="_enhanced")
    print(f"Process complete. Results saved to: {output_path}")
    
    # Display a snippet of the results
    print("\nSample Output:")
    # httpbin returns the data sent in the 'json' field of its response
    print(df_enhanced[["id", "title", "api_response", "exception_summary"]].head())

if __name__ == "__main__":
    main()
