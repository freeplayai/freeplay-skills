# Logging Verification Guide

Use MCP tools to verify logging quality after integration.

## MCP Tools for Verification

- `search_completions` — Verify completions are being logged
- `search_sessions` — Verify sessions are being created
- `search_traces` — Verify traces are being logged (for agents)
- `find_logging_issues` — Check logging quality and identify gaps

(Full names: `mcp__freeplay-mcp-v1__<tool_name>`)

## Verification Steps

1. **Search for recent completions** with `search_completions(project_id, limit=10)`
2. **Search for sessions** with `search_sessions(project_id, limit=10)`
3. **Search for traces** (if agent) with `search_traces(project_id, limit=10)`
4. **Run quality check** with `find_logging_issues(project_id, template_name, environment)`

## Display Results

```
LOGGING VERIFICATION
═══════════════════════════════════════════════════════════════

✓ Completions are being logged
✓ Session IDs present
✓ Model and provider logged
⚠ 40% of completions missing prompt_template linkage

RECOMMENDATION:
  Link completions to Freeplay prompt templates to enable:
  - A/B testing between prompt versions
  - Prompt iteration tracking
  - Version-specific analytics

═══════════════════════════════════════════════════════════════
```

## Common Issues

- No completions appearing → Check API key, project ID, network connectivity
- Missing session IDs → Session not being created or passed correctly
- Missing template linkage → `prompt_version_info` not included in recording
- Missing traces → `create_trace()` not being called (expected for agents)
