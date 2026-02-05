#!/usr/bin/env python3
"""Import test cases from CSV or JSONL files into Freeplay datasets.

Handles batching automatically (100 test cases per request).
Supports both prompt-level and agent-level datasets.
"""

import argparse
import json
import csv
import os
import sys
import requests
from typing import List, Dict, Any

from secrets import SecretString, safe_error_message


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load test cases from JSONL file."""
    test_cases = []
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                test_cases.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                sys.exit(1)
    return test_cases


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """Load test cases from CSV file.

    Expected format:
    - Columns starting with "inputs." become inputs dict keys
    - "output" column becomes the output field
    - Other columns become metadata

    Example CSV:
    inputs.question,inputs.context,output,category,priority
    "What is...","User context","Expected response","refunds","high"
    """
    test_cases = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, 1):
            test_case = {
                "inputs": {},
                "output": row.get("output", ""),
                "metadata": {}
            }

            for key, value in row.items():
                if key.startswith("inputs."):
                    input_key = key.replace("inputs.", "")
                    test_case["inputs"][input_key] = value
                elif key == "output":
                    test_case["output"] = value
                elif key:  # Skip empty column names
                    test_case["metadata"][key] = value

            if not test_case["inputs"]:
                print(f"Warning: Row {row_num} has no inputs", file=sys.stderr)

            test_cases.append(test_case)

    return test_cases


def batch_upload(
    test_cases: List[Dict[str, Any]],
    dataset_type: str,
    dataset_id: str,
    api_base: str,
    project_id: str,
    api_key: SecretString,
    batch_size: int = 100
) -> None:
    """Upload test cases in batches.

    Args:
        test_cases: List of test case dicts
        dataset_type: "prompt-datasets" or "agent-datasets"
        dataset_id: The dataset ID
        api_base: Freeplay API base URL
        project_id: Freeplay project ID
        api_key: SecretString containing the Freeplay API key
        batch_size: Number of test cases per batch (max 100)
    """
    headers = {
        "Authorization": f"Bearer {api_key.get()}",
        "Content-Type": "application/json"
    }

    total_batches = (len(test_cases) + batch_size - 1) // batch_size
    successful_batches = 0
    total_uploaded = 0

    for i in range(0, len(test_cases), batch_size):
        batch = test_cases[i:i + batch_size]
        batch_num = i // batch_size + 1

        url = f"{api_base}/api/v2/projects/{project_id}/{dataset_type}/{dataset_id}/test-cases/bulk"

        try:
            response = requests.post(
                url,
                headers=headers,
                json={"data": batch},
                timeout=30
            )

            if response.status_code == 201:
                result = response.json()
                uploaded = len(result.get('data', []))
                total_uploaded += uploaded
                successful_batches += 1
                print(f"✓ Batch {batch_num}/{total_batches}: Uploaded {uploaded} test cases")
            else:
                print(f"✗ Batch {batch_num}/{total_batches} failed: {response.status_code}", file=sys.stderr)
                print(f"  Response: {safe_error_message(response.text)}", file=sys.stderr)

        except requests.RequestException as e:
            print(f"✗ Batch {batch_num}/{total_batches} failed: {e}", file=sys.stderr)

    print(f"\n{'='*50}")
    print(f"Upload complete: {total_uploaded}/{len(test_cases)} test cases uploaded")
    print(f"Successful batches: {successful_batches}/{total_batches}")

    if total_uploaded < len(test_cases):
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Import test cases from CSV or JSONL files into Freeplay datasets"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to CSV or JSONL file"
    )
    parser.add_argument(
        "--dataset-id",
        required=True,
        help="Freeplay dataset ID"
    )
    parser.add_argument(
        "--type",
        choices=["prompt", "agent"],
        required=True,
        help="Dataset type: 'prompt' for prompt-datasets, 'agent' for agent-datasets"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of test cases per batch (max 100, default: 100)"
    )

    args = parser.parse_args()

    # Validate batch size
    if args.batch_size < 1 or args.batch_size > 100:
        print("Error: batch-size must be between 1 and 100", file=sys.stderr)
        sys.exit(1)

    # Get environment variables
    api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))
    api_base = os.environ.get("FREEPLAY_API_BASE")
    project_id = os.environ.get("FREEPLAY_PROJECT_ID")

    if not api_key:
        print("Error: FREEPLAY_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not api_base:
        print("Error: FREEPLAY_API_BASE environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not project_id:
        print("Error: FREEPLAY_PROJECT_ID environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Load test cases
    file_ext = args.file.lower().split('.')[-1]

    print(f"Loading test cases from {args.file}...")

    if file_ext == 'jsonl':
        test_cases = load_jsonl(args.file)
    elif file_ext == 'csv':
        test_cases = load_csv(args.file)
    else:
        print(f"Error: Unsupported file type '.{file_ext}'. Use .csv or .jsonl", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Loaded {len(test_cases)} test cases")

    if not test_cases:
        print("Error: No test cases found in file", file=sys.stderr)
        sys.exit(1)

    # Determine dataset type path
    dataset_type = "prompt-datasets" if args.type == "prompt" else "agent-datasets"

    # Upload in batches
    print(f"\nUploading to {dataset_type}/{args.dataset_id}...")
    batch_upload(
        test_cases=test_cases,
        dataset_type=dataset_type,
        dataset_id=args.dataset_id,
        api_base=api_base,
        project_id=project_id,
        api_key=api_key,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
