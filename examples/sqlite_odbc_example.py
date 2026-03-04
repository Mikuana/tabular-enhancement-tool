import tabular_enhancement_tool as tet
import os
import pandas as pd

def main():
    # 1. Path to our sample data
    csv_file = os.path.join(os.path.dirname(__file__), "users_to_enrich.csv")
    db_file = os.path.join(os.path.dirname(__file__), "sample_data.db")
    
    # SQLite connection URL
    db_url = f"sqlite:///{db_file}"
    
    # 2. Read the tabular file
    print(f"Reading {csv_file}...")
    df = tet.read_tabular_file(csv_file)
    
    # 3. SQLAlchemy/ODBC Configuration
    # We want to match rows by the 'email' column and fetch all columns from the 'users' table.
    table_name = "users"
    mapping = ["email"]
    
    print(f"Enhancing data via SQLite database ({db_url})...")
    enhancer = tet.ODBCEnhancer(
        connection_url=db_url,
        mapping=mapping,
        table_name=table_name,
        max_workers=5
    )
    
    # 4. Process the DataFrame
    # Method 1: Default (Flattened)
    # Database rows will be added as individual columns.
    print("\n--- Method 1: Default (Flattened) ---")
    df_flattened = enhancer.process_dataframe(df)
    print("New columns from DB:", [c for c in df_flattened.columns if c not in df.columns])
    print(df_flattened.head())

    # Method 2: Non-Flattened
    # Results will be contained within a single 'odbc_response' column.
    print("\n--- Method 2: Non-Flattened ---")
    enhancer_no_flatten = tet.ODBCEnhancer(
        connection_url=db_url,
        mapping=mapping,
        table_name=table_name,
        max_workers=5,
        flatten_response=False
    )
    df_non_flattened = enhancer_no_flatten.process_dataframe(df)
    print(df_non_flattened[["email", "odbc_response", "exception_summary"]].head())

    # 5. Save the results (using flattened as preferred)
    output_path = tet.save_tabular_file(df_flattened, csv_file, suffix="_enriched")
    print(f"\nProcess complete. Results saved to: {output_path}")

if __name__ == "__main__":
    main()
