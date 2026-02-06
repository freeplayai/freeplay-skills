#!/usr/bin/env python3
"""Get deployed prompts from Freeplay.

Lists all prompt templates deployed to each environment (dev, staging, production).

Usage:
    uv run --with requests python3 scripts/get_deployed_prompts.py
    uv run --with requests python3 scripts/get_deployed_prompts.py --project-id proj_123

Environment variables required:
    FREEPLAY_API_KEY     - Your Freeplay API key
    FREEPLAY_API_BASE    - API base URL (e.g., https://api.freeplay.ai)
"""

import argparse
import json
import os
import sys

import requests

# Add scripts directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from secrets import SecretString


def get_config(project_id_arg=None):
    """Get Freeplay configuration from environment variables and CLI args."""
    api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))
    api_base = os.environ.get("FREEPLAY_API_BASE")
    project_id = project_id_arg

    missing = []
    if not api_key:
        missing.append("FREEPLAY_API_KEY")
    if not api_base:
        missing.append("FREEPLAY_API_BASE")

    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    if not project_id:
        print("No project ID provided. Use --project-id <id>.")
        print("Fetching available projects...\n")
        list_projects(api_base, api_key)
        sys.exit(1)

    return api_key, api_base, project_id


def list_projects(api_base, api_key):
    """List available Freeplay projects."""
    headers = get_headers(api_key)
    url = f"{api_base}/api/v2/projects"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json().get("data", response.json() if isinstance(response.json(), list) else [])
        if not projects:
            print("No projects found.")
            return
        print("Available projects:")
        for proj in projects:
            name = proj.get("name", "unnamed")
            proj_id = proj.get("id", "unknown")
            print(f"  - {name} (ID: {proj_id})")
        print(f"\nRe-run with: --project-id <id>")
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching projects: {e}")
        sys.exit(1)


def get_headers(api_key: SecretString) -> dict:
    """Get request headers with authentication."""
    return {
        "Authorization": f"Bearer {api_key.get()}",
        "Content-Type": "application/json",
    }


def get_deployed_prompts_by_environment(api_base: str, project_id: str, headers: dict, environment: str) -> list:
    """Get all prompt templates deployed to a specific environment."""
    url = f"{api_base}/api/v2/projects/{project_id}/prompt-templates/environments/{environment}"
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return []

    response.raise_for_status()
    return response.json()


def get_all_prompt_templates(api_base: str, project_id: str, headers: dict) -> list:
    """Get all prompt templates in the project."""
    url = f"{api_base}/api/v2/projects/{project_id}/prompt-templates"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def format_prompt_content(content: list) -> str:
    """Format prompt template content for display."""
    if not content:
        return "  (no content)"

    lines = []
    for msg in content:
        role = msg.get("role", "unknown")
        text = msg.get("content", "")
        # Truncate long content
        if len(text) > 200:
            text = text[:200] + "..."
        lines.append(f"    [{role}]: {text}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Get deployed prompts from Freeplay"
    )
    parser.add_argument(
        "--project-id",
        help="Freeplay project ID (lists available projects if not provided)"
    )
    args = parser.parse_args()

    api_key, api_base, project_id = get_config(project_id_arg=args.project_id)
    headers = get_headers(api_key)

    environments = ["dev", "staging", "production"]

    print(f"Fetching deployed prompts for project: {project_id}\n")
    print("=" * 60)

    for env in environments:
        print(f"\n Environment: {env.upper()}")
        print("-" * 40)

        try:
            prompts = get_deployed_prompts_by_environment(api_base, project_id, headers, env)

            if not prompts:
                print("  No prompts deployed to this environment")
                continue

            for prompt in prompts:
                name = prompt.get("prompt_template_name", "unnamed")
                version_name = prompt.get("version_name", "")
                version_id = prompt.get("prompt_template_version_id", "")[:8]
                model = prompt.get("model", "unknown")
                provider = prompt.get("provider", "unknown")
                content = prompt.get("content", [])

                print(f"\n  {name}")
                if version_name:
                    print(f"     Version: {version_name} ({version_id}...)")
                else:
                    print(f"     Version ID: {version_id}...")
                print(f"     Model: {provider}/{model}")
                print(f"     Content:")
                print(format_prompt_content(content))

        except requests.exceptions.HTTPError as e:
            print(f"  Error fetching prompts: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
