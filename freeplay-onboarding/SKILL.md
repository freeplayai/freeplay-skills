---
name: freeplay-onboarding
description: "Complete guided onboarding to Freeplay \u2014 analyzes codebase, migrates prompts, and integrates logging. Use whenever the user says 'onboard to Freeplay', 'set up Freeplay', 'get started with Freeplay', 'integrate Freeplay', or wants end-to-end setup."
---

# /freeplay-onboarding

Orchestrate the complete Freeplay onboarding flow with checkpoint-based progression.

This is the **meta-skill** that orchestrates:
1. `/freeplay-plan` - Analyze codebase
2. `/prompt-migration` - Migrate prompts
3. `/record-to-freeplay` - Integrate logging

## Flow

Check state -> Display progress -> Execute phases (plan -> migrate -> log) with approval gate between each. Progress saved to `.freeplay/` after each phase.

## Workflow

### Step 1: Check Existing State

Look for `.freeplay/` directory and existing state files.

Reference `_reference/ui-examples.md` for UI formatting examples throughout onboarding. When interacting with Freeplay, prefer using the MCP server tools (`mcp__freeplay-mcp-v1__*`) first. For endpoints or operations not covered by MCP tools, see `_shared/FREEPLAY_API_REFERENCE.md`.

**State detection:**
- `.freeplay/environment-config.json` exists -> Environment configured
- `.freeplay/analysis.json` exists -> Phase 1 complete
- `.freeplay/migration-manifest.json` exists -> Phase 2 complete
- `.freeplay/integration-report.json` exists -> Phase 3 complete

### Step 1.5: Configure Environment

If `.freeplay/environment-config.json` doesn't exist, follow the configuration workflow in `_shared/environment-config.md`. This creates the config file with domain, API key, project ID, and URLs, and prompts the user to set environment variables.

### Step 2: Display Progress & Options

- If starting fresh: Welcome message with 3 phases listed
- If resuming: Show completed phases with results, offer to continue or re-run

### Step 3: Execute Phases Sequentially

Run each phase with approval gates between them:

#### Phase 1: Analyze Codebase

Execute the `/freeplay-plan` workflow:

1. Scan codebase for prompts, frameworks, telemetry
2. Build prompt inventory
3. Generate migration plan
4. Present plan to user
5. Get user approval

**Approval gate:** User must approve the analysis before proceeding. Show summary of findings and ask to continue.

#### Phase 2: Migrate Prompts

Execute the `/prompt-migration` workflow:

1. Load approved analysis
2. Select Freeplay project
3. Generate migration preview
4. Get batch approval
5. Execute migration
6. Generate manifest

**Approval gate:** User must confirm prompts look correct in Freeplay before continuing.

Show completion summary:
```
Phase 2 complete!

  Prompts migrated to Freeplay
  Deployed to latest environment
  Manifest saved to .freeplay/migration-manifest.json

Please verify your prompts in Freeplay, then continue.

Continue to Phase 3 (Integrate Logging)? [y/n]
```

Use Quick Links from `_shared/environment-config.md` to show relevant project URLs.

#### Phase 3: Integrate Logging

Execute the `/record-to-freeplay` workflow:

1. Load framework detection
2. Present integration plan
3. Generate framework-specific code
4. Apply changes with approval
5. Guide testing
6. Verify with Freeplay API

**Approval gate:** User must confirm traces appear in Freeplay.

### Step 4: Handle Interruptions

If user wants to stop mid-onboarding, show progress saved and explain how to resume.

### Step 5: Handle Phase Skipping

If user wants to skip a phase, warn about implications (especially for prompt migration) and confirm.

### Step 6: Final Summary

Display completion message with summary of changes, links, files, next steps, and documentation. See `_reference/ui-examples.md` for detailed format. Use Quick Links from `_shared/environment-config.md` for project URLs.

### Step 7: Generate Onboarding Report

Create/update `.freeplay/onboarding-status.json` tracking all phases. See `_reference/report-schemas.md` for the schema.

## State Management

**Reads:**
- `.freeplay/environment-config.json` - Credentials and URLs
- `.freeplay/analysis.json` - Phase 1 status
- `.freeplay/migration-manifest.json` - Phase 2 status
- `.freeplay/integration-report.json` - Phase 3 status
- `.freeplay/onboarding-status.json` - Overall status

**Creates/Updates:**
- `.freeplay/onboarding-status.json` - Track overall progress
- Delegates to sub-skills for other state files

## Error Recovery

**If a phase fails:**
- Log the error to `.freeplay/logs/`
- Offer to retry or skip
- Preserve completed phases

**If user interrupts:**
- Save current state immediately
- Provide clear resume instructions

**If state is corrupted:**
- Detect invalid JSON
- Offer to backup and restart that phase

## Notes

- This skill coordinates the other skills but doesn't duplicate their logic
- Each phase is self-contained and can be run independently
- State files in `.freeplay/` enable resumability
- User can always run individual skills directly if preferred
