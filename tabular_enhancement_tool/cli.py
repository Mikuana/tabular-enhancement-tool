from . import core as tet
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Process tabular data and enhance it via API.')
    parser.add_argument('input_file', help='Path to the input tabular file (CSV, Excel, TSV, TXT)')
    parser.add_argument('--api_url', required=True, help='URL of the API to call')
    parser.add_argument('--mapping', required=True, help='JSON string mapping API fields to DataFrame columns. e.g. \'{"id": "user_id"}\'')
    parser.add_argument('--max_workers', type=int, default=5, help='Number of threads for parallel processing')
    parser.add_argument('--auth_type', choices=['basic', 'bearer', 'apikey'], help='Authentication type')
    parser.add_argument('--auth_user', help='Username for Basic Auth')
    parser.add_argument('--auth_pass', help='Password for Basic Auth')
    parser.add_argument('--auth_token', help='Token for Bearer or API Key auth')
    parser.add_argument('--auth_header', default='X-API-Key', help='Header name for API Key auth (default: X-API-Key)')
    
    args = parser.parse_args()

    import json
    try:
        mapping = json.loads(args.mapping)
    except json.JSONDecodeError:
        print("Error: Invalid JSON mapping string.")
        return sys.exit(1)

    auth = None
    headers = None
    if args.auth_type == 'basic':
        if not args.auth_user or not args.auth_pass:
            print("Error: --auth_user and --auth_pass are required for basic auth.")
            return sys.exit(1)
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth(args.auth_user, args.auth_pass)
    elif args.auth_type == 'bearer':
        if not args.auth_token:
            print("Error: --auth_token is required for bearer auth.")
            return sys.exit(1)
        headers = {"Authorization": f"Bearer {args.auth_token}"}
    elif args.auth_type == 'apikey':
        if not args.auth_token:
            print("Error: --auth_token is required for apikey auth.")
            return sys.exit(1)
        headers = {args.auth_header: args.auth_token}

    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.")
        return sys.exit(1)

    print(f"Reading file {args.input_file}...")
    df = tet.read_tabular_file(args.input_file)
    
    print(f"Enhancing data using API {args.api_url}...")
    enhancer = tet.TabularEnhancer(
        args.api_url, 
        mapping, 
        max_workers=args.max_workers,
        auth=auth,
        headers=headers
    )
    df_enhanced = enhancer.process_dataframe(df)

    output_path = tet.save_tabular_file(df_enhanced, args.input_file)
    print(f"Done! Enhanced file saved to {output_path}")

if __name__ == '__main__':
    main()
