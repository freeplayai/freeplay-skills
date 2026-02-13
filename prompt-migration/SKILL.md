---
name: prompt-migration
description: "Migrate prompts from code into Freeplay for version control, A/B testing, and centralized management. Use whenever the user wants to move prompts, manage templates, set up prompt management, or mentions 'migrate prompts', 'prompt versioning', 'prompt templates', or wants to organize their prompts."
---

# /prompt-migration

Migrate prompts to Freeplay based on the approved analysis plan.

## When to Use

- User has run `/freeplay-plan` and approved the analysis
- User wants to migrate prompts to Freeplay
- `.freeplay/analysis.json` exists with an approved plan

## Prerequisites

- `.freeplay/analysis.json` must exist (created by `/freeplay-plan`)
- Freeplay MCP server must be connected
- User must have Freeplay API credentials configured

## Reference Materials

When interacting with Freeplay, prefer using the MCP server tools (`mcp__freeplay-mcp-v1__*`) first. For endpoints or operations not covered by MCP tools (e.g. getting bound versions, detailed request/response shapes), see `_shared/FREEPLAY_API_REFERENCE.md`.

## MCP Tools used in this skill

- `create_prompt_version_and_deploy` -- Create/deploy prompt templates
- `list_projects` -- List available projects
- `list_prompt_templates` -- Check existing templates
- `get_prompt_version` -- Verify migrated prompts

(Full names: `mcp__freeplay-mcp-v1__<tool_name>`)

## Workflow

### Step 1: Load Analysis & Environment Config

**Load analysis:**

Read `.freeplay/analysis.json` and validate it exists, is valid JSON, contains prompts with migration strategies, and has a user-approved plan.

If analysis doesn't exist, inform user: "No analysis found. Run `/freeplay-plan` first to analyze your codebase."

**Load environment configuration:**

Follow `_shared/environment-config.md` to load or create `.freeplay/environment-config.json`. Store config in memory for use throughout migration.

### Step 2: Select Freeplay Project

**Check for pre-configured project:**

If `FREEPLAY_PROJECT_ID` is set in environment config, confirm with user:

```
Using pre-configured Freeplay project: {project_id}
View at: {FREEPLAY_BASE_URL}/projects/{project_id}/home

Continue with this project? [y/n]
```

**If no project configured or user wants a different one:**

Use `list_projects` to show available projects and ask user to choose. Project creation must be done via the Freeplay UI -- guide user there if needed, then re-run `list_projects`.

Optionally use `list_prompt_templates` to check for existing templates and avoid naming conflicts.

### Step 3: Prepare Migration Batch

Before converting any prompts, read `_shared/prompt-mapping-guide.md` and `_reference/convert-to-mustache.md`.

Why this matters: Freeplay has a specific message structure (role, content, kind) and uses Mustache templating. The mapping guide contains the decision tree for handling all prompt patterns, and the conversion guide covers syntax transformation rules. Getting these wrong means broken prompts.

For each prompt marked as `direct` or `needs_review` in the analysis:

1. **Load metadata** from analysis.json (structure, variables, tools, model config)

2. **Determine structure** using the decision tree in the mapping guide:
   - Single string -- Analyze content (pure instructions? user variables? examples?)
   - Pre-structured -- Direct mapping with normalization
   - History loop -- Replace with `{"kind": "history"}` placeholder
   - Tools/schemas -- Extract to separate parameters
   - Ambiguous -- Flag for user review with proposed structure

3. **Apply transformations**:
   - Convert variable syntax (see `_reference/convert-to-mustache.md`)
   - Normalize roles to lowercase
   - Replace history loops with placeholder (NOT a variable)
   - Confirm complex logic conversions with user

4. **Handle variables intelligently:**
   1. Extract variables already present in the proposed messages
   2. Check analysis.json for call-site variables not yet in messages
   3. For each missing call-site variable, add to appropriate message (user input -> user message, context -> system message)
   4. If analysis flagged "needs_user_input", confirm with user before migration

5. **Extract features** to parameters:
   - Tools -> `tool_schema`
   - Output formats -> `output_schema`
   - Model settings -> `llm_parameters`

6. **Build API call** with required fields (template_name, prompt_messages, model, provider, environments) and optional fields (version_name, llm_parameters, tool_schema, output_schema)

### Step 3.5: Apply Best Practices

Follow role and variable placement guidelines in `_shared/prompt-mapping-guide.md` (sections: Role Inference Heuristics, Variable Classification).

Present improvements as suggestions, not requirements. Ask the user if they'd like restructuring suggestions before applying.

### Step 3.7: Validate Before Presenting

Check each prompt against `_reference/validation-rules.md`. The most common mistakes are: uppercase roles, wrong variable syntax ({var} instead of {{var}}), and using {{history}} instead of {"kind": "history"}. Auto-correct where possible, flag for user review otherwise.

### Step 4: Generate Migration Preview

Show each prompt's proposed Freeplay structure. For format examples, see `_reference/migration-preview-examples.md`.

Include: detected pattern, mapping decision, validation status, variables, transformations.
Use simplified format for quick overview, detailed format for complex or user-requested cases.

### Step 5: Handle User Edits

If user wants to edit:
- Allow renaming templates
- Allow adding/removing variables
- Allow changing model/provider
- Allow skipping specific prompts

Update the migration batch with changes.

### Step 6: Execute Migration & Verify

For each approved prompt, use `create_prompt_version_and_deploy`:

```
Parameters:
  - project_id: [selected project]
  - template_name: [prompt name]
  - prompt_messages: [JSON array of messages]
  - model: [detected or default model]
  - provider: [detected or default provider]
  - environments: "latest"
  - create_if_not_exists: true
```

Show progress as each prompt is created:

```
Migrating prompts...

[1/4] main_system_prompt - Created
      View in Freeplay: {FREEPLAY_BASE_URL}/projects/{project_id}/templates/{template_id}

[2/4] chat_with_history - Created
...

Migration complete! 4/4 prompts created.
```

**Verify each migration** using `get_prompt_version`. Check message count, structure, variables, tool/output schemas, and model/provider. Report any mismatches:

```
Verifying migration...

main_system_prompt - Messages: 1, Variables: 2, Model: gpt-4o
chat_with_history - Messages: 3 (with history), Variables: 1, Model: gpt-4
tool_calling_prompt - Tool schema mismatch (expected 3, got 2)

3/4 verified. Review flagged items.
```

### Step 7: Handle Errors

If a migration fails:
- Log the error and continue with remaining prompts
- Report failures at the end
- Offer to retry failed prompts or skip them

### Step 8: Generate Migration Manifest

Create `.freeplay/migration-manifest.json`:

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
        "Variable syntax: jinja -> freeplay",
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

### Step 9: Provide Next Steps

```
MIGRATION COMPLETE

  4 prompts migrated to Freeplay
  1 prompt skipped (requires manual migration)

NEXT STEPS:
  1. Open Freeplay and verify your prompts look correct
  2. Test each prompt in the Freeplay playground
  3. When ready, deploy to production in the Freeplay UI
  4. Run /record-to-freeplay to set up logging integration
     OR run /freeplay-onboarding to continue full onboarding

Quick Links:
  Project Home:     {FREEPLAY_BASE_URL}/projects/{project_id}/home
  Prompt Templates: {FREEPLAY_BASE_URL}/projects/{project_id}/templates
  Observability:    {FREEPLAY_BASE_URL}/projects/{project_id}/sessions
```

## State Management

**Reads:** `.freeplay/analysis.json` -- The approved migration plan

**Creates:** `.freeplay/migration-manifest.json` -- Record of what was migrated

## Error Handling

- If analysis.json missing: Direct user to run `/freeplay-plan` first
- If no Freeplay connection: Guide user to configure MCP server
- If API auth fails: Guide user to check FREEPLAY_API_KEY
- If project not found: Offer to list available projects
- If prompt creation fails: Log error, continue with others, report at end

## Anti-Pattern Guidance

If user asks about keeping prompts in both code AND Freeplay:
> "Use Freeplay as the single source of truth. This enables version history, A/B testing, non-engineer editing, and environment-specific deployments. Your code should fetch prompts from Freeplay at runtime."

If user wants to version prompts in Git AND Freeplay:
> "Freeplay handles versioning automatically -- each edit creates a new version with full history. Your code repo should contain integration code, not prompt content."
