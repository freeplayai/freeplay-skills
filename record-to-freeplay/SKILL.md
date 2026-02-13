---
name: record-to-freeplay
description: Integrate Freeplay logging, tracing, and observability into an LLM application. Use whenever the user mentions recording LLM calls, adding observability, capturing traces, logging to Freeplay, monitoring LLM usage, or wants a dashboard — even if they don't say 'Freeplay'. Also use after prompt migration, or for observability-only setups.
---

# /record-to-freeplay

Integrate Freeplay logging, tracing, and observability into an LLM application.

## Prerequisites

- `.freeplay/analysis.json` should exist (from `/freeplay-plan`). If missing, run quick framework detection or ask user.
- `.freeplay/migration-manifest.json` is helpful for prompt template IDs (from `/prompt-migration`).
- Freeplay MCP server connected.

## Key Concepts

**Freeplay Observability Hierarchy:**
```
Session (entire user interaction / conversation)
  └── Trace (logical grouping: agent workflow, multi-step task)
        ├── Completion (single LLM API call)
        └── Tool Trace (function/tool call, kind="tool")
```

See `_reference/general-logging-guide.md` for the primary integration reference. See `_reference/patterns/freeplay-patterns.md` for hierarchy guidance. When interacting with Freeplay, prefer using the MCP server tools (`mcp__freeplay-mcp-v1__*`) first. For endpoints or operations not covered by MCP tools (e.g. recording completions, traces, feedback, metadata updates), see `_shared/FREEPLAY_API_REFERENCE.md`.

## MCP Tool Names

Full names are used for tool calls. Short names used in this document for readability:

| Short Name | Full MCP Tool Name |
|---|---|
| `search_completions` | `mcp__freeplay-mcp-v1__search_completions` |
| `search_sessions` | `mcp__freeplay-mcp-v1__search_sessions` |
| `search_traces` | `mcp__freeplay-mcp-v1__search_traces` |
| `find_logging_issues` | `mcp__freeplay-mcp-v1__find_logging_issues` |

## Framework Support Matrix

| Framework | Integration Type | Package | Complexity |
|-----------|------------------|---------|------------|
| LangGraph | Auto-instrumented (OTel) | `freeplay-langgraph` | Simple |
| Google ADK | Auto-instrumented (OTel + plugin) | `freeplay-python-adk` | Simple |
| Vercel AI SDK | OpenTelemetry + helpers | `@freeplayai/vercel` | Simple |
| Vanilla OpenAI | Helper functions | `freeplay` | Moderate |
| Vanilla Anthropic | Helper functions | `freeplay` | Moderate |
| LangChain | Via LangGraph package | `freeplay-langgraph` | Simple |

## Workflow

### Step 1: Load Context

Load environment config from `.freeplay/environment-config.json`. See `../_shared/environment-config.md` for the loading workflow and fallback dialog if config is missing.

Read `.freeplay/analysis.json` for detected framework, existing telemetry, LLM providers, and file locations.

Read `.freeplay/migration-manifest.json` (if exists) for project ID and migrated template names/IDs.

### Step 2: Present Integration Plan

Based on detected framework, show the integration approach. Adapt the structure mapping and SDK approach to the actual detected framework -- do not hardcode a specific framework.

```
LOGGING INTEGRATION PLAN
═══════════════════════════════════════════════════════════════

Framework Detected: [detected framework] ([confidence])
LLM Providers: [detected providers]
Existing Telemetry: [any existing telemetry or "None"]

FREEPLAY STRUCTURE MAPPING:
┌─────────────────┬─────────────────────────────────────────────┐
│ Freeplay        │ Your Code                                   │
├─────────────────┼─────────────────────────────────────────────┤
│ Session         │ [map to user's concept, e.g. conversation]  │
│ Trace           │ [map to user's concept, e.g. graph invoke]  │
│ Completion      │ [map to user's concept, e.g. each LLM call] │
└─────────────────┴─────────────────────────────────────────────┘

WHAT WILL BE LOGGED:
  Sessions, traces, completions, tool calls, prompt template linkage

INTEGRATION APPROACH:
  Package: [appropriate package from framework matrix]
  Pattern: [brief description of approach]

FILES TO MODIFY:
  ~ [list files that will change]

═══════════════════════════════════════════════════════════════

Approve this plan? [y/n]
```

### Step 3: Generate Integration Code

Before writing any code, read `_reference/general-logging-guide.md`.

Why this matters: The Freeplay SDK has a specific API (e.g., `get_formatted()`, `session.create_trace()`, `RecordPayload`) that doesn't follow typical patterns. Relying on general knowledge will produce broken code with made-up method names. The reference guide contains the actual, tested helper functions to adapt.

For framework-specific patterns, also read the relevant integration reference:
- LangGraph: `_reference/integrations/langgraph-complete.md`
- Google ADK: `_reference/integrations/adk-complete.md`
- Vercel AI SDK: `_reference/integrations/vercel-integration.md`
- Vanilla OpenAI/Anthropic: Use patterns from `general-logging-guide.md` directly

The goal is minimal disruption to existing code. Add a small helper function (like `call_and_record` from the reference guide) and wire it into existing call sites. Don't create wrapper classes, abstraction layers, or restructure how the user calls their LLM -- just add recording alongside what they already have.

Why this matters: Users want observability, not a rewrite. If the integration feels invasive, they'll rip it out.

**What to generate:**
1. Freeplay client init (a few lines, added to existing config/setup code)
2. One or two small helper functions (like `call_and_record` from the reference guide)
3. Minimal changes to existing call sites to use the helper or add recording

**What NOT to generate:**
- Wrapper classes or abstraction layers
- New "client" files with extensive initialization/retry logic
- Over-engineered session/trace management classes

Before showing code to the user, verify: uses correct SDK methods from the reference guide, helper functions are small and focused, existing user code is minimally changed, no made-up SDK parameters. If something looks wrong, re-read the reference guide rather than guessing.

### Step 4: Apply Changes

Show the code changes as diffs and get user approval. Changes should be minimal -- adding a few imports, client init, and helper function(s) alongside existing code. Apply changes with user confirmation for each file.

### Step 5: Environment Setup

Provide environment variable instructions. See `_reference/environment-setup.md` for the full template using values from `.freeplay/environment-config.json`.

### Step 6: Test Integration

Guide user through testing:

```
TESTING YOUR INTEGRATION
═══════════════════════════════════════════════════════════════

1. Run your application with a test query

2. Check Freeplay for the logged data:
   View Sessions: {FREEPLAY_BASE_URL}/projects/{FREEPLAY_PROJECT_ID}/sessions

3. Verify the structure looks correct:
   - Session created
   - Trace showing the workflow (if agent)
   - Completions with prompt and response

═══════════════════════════════════════════════════════════════
```

Include Quick Links (see completion summary format in Step 9).

### Step 7: Verify with MCP Tools

Use MCP tools to verify logging quality. See `_reference/verification-guide.md` for the verification workflow, tool usage, display format, and common issues.

### Step 8: Generate Integration Report

Create `.freeplay/integration-report.json`. See `../freeplay-onboarding/_reference/report-schemas.md` for the full schema. Include: framework, files modified, environment variables, logging coverage, verification results, and next steps.

### Step 9: Completion Summary

```
LOGGING INTEGRATION COMPLETE
═══════════════════════════════════════════════════════════════

[check] Added Freeplay helper function(s) to [file]
[check] Wired recording into existing LLM call sites
[check] Verified logging is working

WHAT'S NOW BEING LOGGED:
  - Sessions (conversation continuity)
  - Traces (execution flows)
  - Completions (LLM calls with prompts/responses)
  - Tool calls (inputs and outputs)

═══════════════════════════════════════════════════════════════
Quick Links:
═══════════════════════════════════════════════════════════════

Project Home: {FREEPLAY_BASE_URL}/projects/{FREEPLAY_PROJECT_ID}/home
Observability (Sessions): {FREEPLAY_BASE_URL}/projects/{FREEPLAY_PROJECT_ID}/sessions
Prompt Templates: {FREEPLAY_BASE_URL}/projects/{FREEPLAY_PROJECT_ID}/templates

NEXT STEPS:
  1. Run your application and check sessions appear in Freeplay
  2. Link completions to prompt templates for full tracking
  3. Deploy to production when ready

═══════════════════════════════════════════════════════════════
```

## Post-Integration

For ongoing optimization and insights after integration, see `_reference/ongoing-tools.md`. Key capabilities: prompt optimization via `optimize_prompt`, AI-generated insights via `list_insights`, and periodic logging quality checks via `find_logging_issues`.

**Additional features to mention to user:** code-side evaluations (pass `eval_results` in `RecordPayload`), customer feedback collection (`fp_client.customer_feedback.update`), and prompt bundling for production (`freeplay download` CLI for zero-latency prompt loading).

## State Management

**Reads:** `.freeplay/analysis.json`, `.freeplay/migration-manifest.json`, `.freeplay/environment-config.json`

**Creates:** `.freeplay/integration-report.json`. Modifies existing code files (with approval).

## Error Handling

- If `analysis.json` missing: Run quick framework detection or ask user
- If framework unknown: Ask user which SDK/framework they use
- If code modifications fail: Show error, offer manual instructions
- If verification shows no logs: Debug connectivity, API key, project ID
