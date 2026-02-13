# Report Schemas

JSON schemas for state files created during onboarding.

## onboarding-status.json

```json
{
  "started_at": "ISO timestamp",
  "completed_at": "ISO timestamp",
  "status": "complete",
  "phases": {
    "analysis": {
      "status": "complete",
      "completed_at": "ISO timestamp",
      "output_file": ".freeplay/analysis.json"
    },
    "migration": {
      "status": "complete",
      "completed_at": "ISO timestamp",
      "output_file": ".freeplay/migration-manifest.json",
      "prompts_migrated": 4,
      "prompts_skipped": 1
    },
    "logging": {
      "status": "complete",
      "completed_at": "ISO timestamp",
      "output_file": ".freeplay/integration-report.json",
      "framework": "langgraph"
    }
  },
  "project": {
    "id": "<project-id>",
    "name": "my-project",
    "url": "https://app.freeplay.ai/projects/<project-id>"
  },
  "files_created": [
    ".freeplay/analysis.json",
    ".freeplay/migration-manifest.json",
    ".freeplay/integration-report.json"
  ],
  "files_modified": [
    "agents/main.py"
  ]
}
```

## integration-report.json

```json
{
  "generated_at": "ISO timestamp",
  "framework": "langgraph",
  "integration_type": "freeplay_langgraph_package",
  "files_modified": [
    {
      "path": "agents/main.py",
      "changes": ["Added Freeplay client init and helper", "Added recording calls"]
    }
  ],
  "environment_variables": [
    {
      "name": "FREEPLAY_API_URL",
      "description": "Freeplay API endpoint",
      "value": "https://app.freeplay.ai/api",
      "required": true
    }
  ],
  "logging_coverage": {
    "sessions": true,
    "traces": true,
    "completions": true,
    "tool_calls": true,
    "prompt_template_linkage": "partial"
  },
  "verification": {
    "status": "success",
    "issues_found": 1,
    "issues": ["Some completions missing template linkage"]
  },
  "next_steps": [
    "Add template_name to completion logging for full tracking",
    "Deploy to production when ready",
    "Monitor traces in Freeplay dashboard"
  ]
}
```

## migration-manifest.json

```json
{
  "generated_at": "ISO timestamp",
  "project_id": "<project-id>",
  "project_name": "my-project",
  "environment": "latest",
  "migrated": [
    {
      "original_source": "prompts/system.yaml",
      "template_name": "main_system_prompt",
      "template_id": "tmpl_abc123",
      "version_id": "ver_xyz",
      "url": "https://app.freeplay.ai/prompts/abc123",
      "variables": ["user_name", "context"],
      "model": "gpt-4o",
      "provider": "openai",
      "transformations": [
        "Variable syntax: jinja → freeplay",
        "Whitespace normalized"
      ]
    }
  ],
  "skipped": [],
  "failed": [],
  "warnings": [],
  "next_steps": [
    "Verify prompts in Freeplay UI",
    "Test with sample inputs in playground",
    "Deploy to production when ready",
    "Run /record-to-freeplay to set up logging"
  ]
}
```
