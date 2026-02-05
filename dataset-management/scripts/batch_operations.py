#!/usr/bin/env python3
"""Utility functions for batch operations on Freeplay datasets.

Provides reusable functions for batching large operations that exceed
the 100-item API limit.
"""

import os
import sys
import requests
from typing import List, Dict, Any, Callable


def get_freeplay_config() -> Dict[str, str]:
    """Get Freeplay configuration from environment variables.

    Returns:
        Dict with api_key, api_base, and project_id

    Raises:
        SystemExit if required environment variables are missing
    """
    api_key = os.environ.get("FREEPLAY_API_KEY")
    api_base = os.environ.get("FREEPLAY_API_BASE")
    project_id = os.environ.get("FREEPLAY_PROJECT_ID")

    missing = []
    if not api_key:
        missing.append("FREEPLAY_API_KEY")
    if not api_base:
        missing.append("FREEPLAY_API_BASE")
    if not project_id:
        missing.append("FREEPLAY_PROJECT_ID")

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return {
        "api_key": api_key,
        "api_base": api_base,
        "project_id": project_id
    }


def get_headers(api_key: str) -> Dict[str, str]:
    """Get standard headers for Freeplay API requests."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


def batch_create_test_cases(
    test_cases: List[Dict[str, Any]],
    dataset_type: str,
    dataset_id: str,
    batch_size: int = 100,
    verbose: bool = True
) -> int:
    """Create test cases in batches.

    Args:
        test_cases: List of test case dicts
        dataset_type: "prompt-datasets" or "agent-datasets"
        dataset_id: The dataset ID
        batch_size: Number of items per batch (max 100)
        verbose: Whether to print progress

    Returns:
        Number of successfully created test cases
    """
    config = get_freeplay_config()
    headers = get_headers(config["api_key"])

    total_uploaded = 0
    total_batches = (len(test_cases) + batch_size - 1) // batch_size

    for i in range(0, len(test_cases), batch_size):
        batch = test_cases[i:i + batch_size]
        batch_num = i // batch_size + 1

        url = f"{config['api_base']}/api/v2/projects/{config['project_id']}/{dataset_type}/{dataset_id}/test-cases/bulk"

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
                if verbose:
                    print(f"✓ Batch {batch_num}/{total_batches}: Created {uploaded} test cases")
            else:
                if verbose:
                    print(f"✗ Batch {batch_num}/{total_batches} failed: {response.status_code}", file=sys.stderr)
                    print(f"  Response: {response.text}", file=sys.stderr)

        except requests.RequestException as e:
            if verbose:
                print(f"✗ Batch {batch_num}/{total_batches} failed: {e}", file=sys.stderr)

    return total_uploaded


def batch_delete_test_cases(
    test_case_ids: List[str],
    dataset_type: str,
    dataset_id: str,
    batch_size: int = 100,
    verbose: bool = True
) -> int:
    """Delete test cases in batches.

    Args:
        test_case_ids: List of test case IDs to delete
        dataset_type: "prompt-datasets" or "agent-datasets"
        dataset_id: The dataset ID
        batch_size: Number of items per batch (max 100)
        verbose: Whether to print progress

    Returns:
        Number of successfully deleted test cases
    """
    config = get_freeplay_config()
    headers = get_headers(config["api_key"])

    total_deleted = 0
    total_batches = (len(test_case_ids) + batch_size - 1) // batch_size

    for i in range(0, len(test_case_ids), batch_size):
        batch = test_case_ids[i:i + batch_size]
        batch_num = i // batch_size + 1

        url = f"{config['api_base']}/api/v2/projects/{config['project_id']}/{dataset_type}/{dataset_id}/test-cases/bulk"

        try:
            response = requests.delete(
                url,
                headers=headers,
                json={"test_case_ids": batch},
                timeout=30
            )

            if response.status_code == 200:
                total_deleted += len(batch)
                if verbose:
                    print(f"✓ Batch {batch_num}/{total_batches}: Deleted {len(batch)} test cases")
            else:
                if verbose:
                    print(f"✗ Batch {batch_num}/{total_batches} failed: {response.status_code}", file=sys.stderr)
                    print(f"  Response: {response.text}", file=sys.stderr)

        except requests.RequestException as e:
            if verbose:
                print(f"✗ Batch {batch_num}/{total_batches} failed: {e}", file=sys.stderr)

    return total_deleted


if __name__ == "__main__":
    print("This module provides utility functions for batch operations.")
    print("Import and use the functions in your scripts:")
    print()
    print("  from batch_operations import batch_create_test_cases, batch_delete_test_cases")
    print()
    print("Or use import_testcases.py for CSV/JSONL imports.")
