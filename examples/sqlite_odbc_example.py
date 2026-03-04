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
    df_enhanced = enhancer.process_dataframe(df)
    
    # 5. Save the results
    output_path = tet.save_tabular_file(df_enhanced, csv_file, suffix="_enriched")
    print(f"Process complete. Results saved to: {output_path}")
    
    # Display the results
    print("\nEnhanced Results:")
    # The database results are in the 'odbc_response' column as a dictionary
    print(df_enhanced)

if __name__ == "__main__":
    main()
