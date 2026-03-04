from . import core as tet
import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser(
        description="Process tabular data and enhance it via API or ODBC."
    )
    parser.add_argument(
        "input_file", help="Path to the input tabular file (CSV, Excel, TSV, TXT, Parquet)"
    )

    # API arguments
    api_group = parser.add_argument_group("API Options")
    api_group.add_argument("--api_url", help="URL of the API to call")
    api_group.add_argument(
        "--mapping",
        help='JSON string mapping API fields or SQL parameters to DataFrame columns. e.g. \'{"id": "user_id"}\' or \'["user_id", "name"]\'',
    )
    api_group.add_argument(
        "--auth_type", choices=["basic", "bearer", "apikey"], help="Authentication type"
    )
    api_group.add_argument("--auth_user", help="Username for Basic Auth")
    api_group.add_argument("--auth_pass", help="Password for Basic Auth")
    api_group.add_argument("--auth_token", help="Token for Bearer or API Key auth")
    api_group.add_argument(
        "--auth_header",
        default="X-API-Key",
        help="Header name for API Key auth (default: X-API-Key)",
    )
    api_group.add_argument(
        "--method",
        default="POST",
        choices=["POST", "GET"],
        help="HTTP method to use (default: POST)",
    )

    # SQLAlchemy arguments
    sqlalchemy_group = parser.add_argument_group("SQLAlchemy Options")
    sqlalchemy_group.add_argument("--db_url", help="SQLAlchemy connection URL")
    sqlalchemy_group.add_argument(
        "--table_name", help="Name of the table to query for enhancement"
    )

    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Number of threads for parallel processing",
    )

    args = parser.parse_args()

    import json

    if args.api_url and args.db_url:
        print("Error: Specify either --api_url or --db_url, not both.")
        return sys.exit(1)

    if not args.api_url and not args.db_url:
        print("Error: One of --api_url or --db_url is required.")
        return sys.exit(1)

    try:
        mapping = json.loads(args.mapping) if args.mapping else None
    except json.JSONDecodeError:
        print("Error: Invalid JSON mapping string.")
        return sys.exit(1)

    if args.api_url:
        if not mapping:
            print("Error: --mapping is required for API enhancement.")
            return sys.exit(1)
        if not isinstance(mapping, dict):
            print("Error: --mapping must be a JSON object for API enhancement.")
            return sys.exit(1)

        auth = None
        headers = None
        if args.auth_type == "basic":
            if not args.auth_user or not args.auth_pass:
                print("Error: --auth_user and --auth_pass are required for basic auth.")
                return sys.exit(1)
            from requests.auth import HTTPBasicAuth

            auth = HTTPBasicAuth(args.auth_user, args.auth_pass)
        elif args.auth_type == "bearer":
            if not args.auth_token:
                print("Error: --auth_token is required for bearer auth.")
                return sys.exit(1)
            headers = {"Authorization": f"Bearer {args.auth_token}"}
        elif args.auth_type == "apikey":
            if not args.auth_token:
                print("Error: --auth_token is required for apikey auth.")
                return sys.exit(1)
            headers = {args.auth_header: args.auth_token}

    elif args.db_url:
        if not args.table_name:
            print("Error: --table_name is required for SQLAlchemy enhancement.")
            return sys.exit(1)
        if mapping is not None and not isinstance(mapping, list):
            print("Error: --mapping must be a JSON list for SQLAlchemy enhancement.")
            return sys.exit(1)
        if mapping is None:
            mapping = []

    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.")
        return sys.exit(1)

    print(f"Reading file {args.input_file}...")
    df = tet.read_tabular_file(args.input_file)

    if args.api_url:
        print(f"Enhancing data using API {args.api_url}...")
        enhancer = tet.TabularEnhancer(
            args.api_url,
            mapping,
            max_workers=args.max_workers,
            auth=auth,
            headers=headers,
            method=args.method,
        )
    else:
        print("Enhancing data using SQLAlchemy...")
        enhancer = tet.ODBCEnhancer(
            args.db_url,
            mapping,
            table_name=args.table_name,
            max_workers=args.max_workers,
        )

    df_enhanced = enhancer.process_dataframe(df)

    output_path = tet.save_tabular_file(df_enhanced, args.input_file)
    print(f"Done! Enhanced file saved to {output_path}")


if __name__ == "__main__":
    main()
