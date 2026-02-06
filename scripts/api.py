#!/usr/bin/env python3
"""Shared Freeplay API utilities."""

import sys
import requests
from typing import Dict

from secrets import SecretString


def get_headers(api_key: SecretString) -> Dict[str, str]:
    """Get standard headers for Freeplay API requests.

    Args:
        api_key: SecretString containing the API key
    """
    return {
        "Authorization": f"Bearer {api_key.get()}",
        "Content-Type": "application/json"
    }


def list_projects(api_base: str, api_key: SecretString):
    """List available Freeplay projects."""
    headers = get_headers(api_key)
    url = f"{api_base}/api/v2/projects/all"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json().get("projects", [])
        if not projects:
            print("No projects found.", file=sys.stderr)
            return
        print("Available projects:", file=sys.stderr)
        for proj in projects:
            name = proj.get("name", "unnamed")
            proj_id = proj.get("id", "unknown")
            print(f"  - {name} (ID: {proj_id})", file=sys.stderr)
        print("\nRe-run with: --project-id <id>", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}", file=sys.stderr)
