import argparse
import os
import sys

from . import core as tet


def main():
    parser = argparse.ArgumentParser(
        description="Process tabular data and enhance it via REST API (POST and GET)."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input tabular file (CSV, Excel, TSV, TXT, Parquet)",
    )

    # API arguments
    api_group = parser.add_argument_group("API Options")
    api_group.add_argument("--api_url", required=True, help="URL of the API to call")
    api_group.add_argument(
        "--mapping",
        required=True,
        help=(
            "JSON string mapping API fields to DataFrame columns. "
            'e.g. \'{"id": "user_id"}\''
        ),
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

    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Number of threads for parallel processing",
    )
    parser.add_argument(
        "--no_flatten",
        action="store_true",
        help=(
            "Do not expand response objects into individual columns. "
            "If used, the response will be stored as a single JSON object in "
            "'api_response'."
        ),
    )

    args = parser.parse_args()

    import json

    if not args.api_url:
        print("Error: --api_url is required.")
        return sys.exit(1)

    try:
        mapping = json.loads(args.mapping) if args.mapping else None
    except json.JSONDecodeError:
        print("Error: Invalid JSON mapping string.")
        return sys.exit(1)

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

    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.")
        return sys.exit(1)

    print(f"Reading file {args.input_file}...")
    enhancer = tet.TabularEnhancer(
        api_url=args.api_url,
        mapping=mapping,
        max_workers=args.max_workers,
        auth=auth,
        headers=headers,
        method=args.method,
        flatten_response=not args.no_flatten,
        file_path=args.input_file,
    )
    enhancer.read()

    print(f"Enhancing data using API {args.api_url}...")
    enhancer.enhance()

    output_path = enhancer.save()
    print(f"Done! Enhanced file saved to {output_path}")


if __name__ == "__main__":
    main()
