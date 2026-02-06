#!/usr/bin/env python3
"""Utility functions for batch operations on Freeplay datasets.

Provides reusable functions for batching large operations that exceed
the 100-item API limit.
"""

import os
import sys
import requests
from typing import List, Dict, Any, Callable

from secrets import SecretString, safe_error_message


def get_freeplay_config(project_id: str = None) -> Dict[str, Any]:
    """Get Freeplay configuration from environment variables.

    Args:
        project_id: Project ID (required)

    Returns:
        Dict with api_key (SecretString), api_base, and project_id

    Raises:
        SystemExit if required environment variables are missing
    """
    api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))
    api_base = os.environ.get("FREEPLAY_BASE_URL", "https://app.freeplay.ai")

    missing = []
    if not api_key:
        missing.append("FREEPLAY_API_KEY")
    if not api_base:
        missing.append("FREEPLAY_BASE_URL")

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if not project_id:
        print("No project ID provided. Pass project_id to get_freeplay_config().", file=sys.stderr)
        print("Fetching available projects...\n", file=sys.stderr)
        _list_projects(api_base, api_key)
        sys.exit(1)

    return {
        "api_key": api_key,
        "api_base": api_base,
        "project_id": project_id
    }


def _list_projects(api_base, api_key):
    """List available Freeplay projects."""
    headers = get_headers(api_key)
    url = f"{api_base}/api/v2/projects"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json().get("data", response.json() if isinstance(response.json(), list) else [])
        if not projects:
            print("No projects found.", file=sys.stderr)
            return
        print("Available projects:", file=sys.stderr)
        for proj in projects:
            name = proj.get("name", "unnamed")
            proj_id = proj.get("id", "unknown")
            print(f"  - {name} (ID: {proj_id})", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}", file=sys.stderr)


def get_headers(api_key: SecretString) -> Dict[str, str]:
    """Get standard headers for Freeplay API requests.

    Args:
        api_key: SecretString containing the API key
    """
    return {
        "Authorization": f"Bearer {api_key.get()}",
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
                    print(f"  Response: {safe_error_message(response.text)}", file=sys.stderr)

        except requests.RequestException as e:
            if verbose:
                print(f"✗ Batch {batch_num}/{total_batches} failed: {e}", file=sys.stderr)

    return total_uploaded


if __name__ == "__main__":
    print("This module provides utility functions for batch operations.")
    print("Import and use the functions in your scripts:")
    print()
    print("  from batch_operations import batch_create_test_cases")
    print()
    print("Or use import_testcases.py for CSV/JSONL imports.")
    print()
    print("Note: Deletion operations are not supported through this skill.")
