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
    # By default, responses are automatically flattened into separate columns.
    print("\n--- Method 1: Default (Flattened) ---")
    df_flattened = enhancer.process_dataframe(df)
    print("Flattened columns added:", [c for c in df_flattened.columns if c not in df.columns])
    print(df_flattened.head())

    # You can also opt-out of flattening to keep the response in a single column.
    print("\n--- Method 2: Non-Flattened (Single Column) ---")
    enhancer_no_flatten = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        method="POST",
        max_workers=5,
        flatten_response=False
    )
    df_non_flattened = enhancer_no_flatten.process_dataframe(df)
    print(df_non_flattened[["id", "title", "api_response", "exception_summary"]].head())

    # 5. Save the results (using flattened as the preferred output)
    output_path = tet.save_tabular_file(df_flattened, input_file, suffix="_enhanced")
    print(f"\nProcess complete. Results saved to: {output_path}")

if __name__ == "__main__":
    main()
