import tabular_enhancement_tool as tet
import os


def main():
    # 1. Path to our sample data
    input_file = os.path.join(os.path.dirname(__file__), "posts_data.csv")

    # 2. Read the tabular file
    print(f"Reading {input_file}...")
    df = tet.read_tabular_file(input_file)

    # 3. HTTPBin Auth Example (POST)
    # This example demonstrates a POST request with an Authorization header (Bearer Token).
    # Since httpbin doesn't strictly validate tokens for all endpoints,
    # we use the /post endpoint which allows us to send a Bearer Token in the headers.
    token = "your_secret_token_here"
    api_url = "https://httpbin.org/post"

    # The mapping defines which CSV columns map to the JSON payload fields
    mapping = {"title": "title", "body": "body", "userId": "userId"}

    print(f"Enhancing data via HTTPBin API (POST with Bearer Token Auth)...")
    
    # We provide the token via the 'headers' parameter.
    enhancer = tet.TabularEnhancer(
        api_url=api_url,
        mapping=mapping,
        method="POST",
        headers={"Authorization": f"Bearer {token}"},
        max_workers=5
    )

    # 4. Process the DataFrame
    # Authenticated requests work exactly like standard ones.
    df_enhanced = enhancer.process_dataframe(df)

    # 5. Show results
    print("\n--- Authenticated POST Results ---")
    print(df_enhanced.head())

    # 6. Bearer Token Example (Optional pattern)
    # If using a Bearer token, you would use headers instead of the auth tuple:
    # token = "your_bearer_token_here"
    # enhancer_bearer = tet.TabularEnhancer(
    #     api_url="https://api.yourservice.com/v1/resource",
    #     mapping=mapping,
    #     method="POST",
    #     headers={"Authorization": f"Bearer {token}"}
    # )

    print("\nProcess complete.")


if __name__ == "__main__":
    main()
