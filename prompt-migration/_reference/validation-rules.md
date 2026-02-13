# Prompt Validation Rules

Validate every prompt before presenting to user or executing migration.

## Required Checks

1. **Roles are lowercase** — `"system"`, not `"System"` or `"SYSTEM"`
2. **Variables use Mustache syntax** — `{{var}}`, not `{var}` or `{{ var }}`
3. **History uses placeholder** — `{"kind": "history"}`, NOT `{{history}}`
4. **No logic in templates** — Conditionals/loops belong in code, not prompts
5. **Tool schemas extracted** — Tool definitions go in `tool_schema` parameter, not in message content
6. **Output schemas extracted** — Structured output definitions go in `output_schema` parameter
7. **All variables from analysis.json are present** — Cross-reference detected variables
8. **Message order is logical** — System → history → user (typical order)
9. **Original meaning preserved** — Changes should be minimal, focused on Freeplay representation

## Auto-Correctable Issues

These can be fixed automatically without user input:
- Uppercase roles → lowercase
- `{var}` → `{{var}}`
- Extra whitespace in variable tags

## Needs User Review

Flag for manual review if:
- Conditional logic in template that can't be simplified
- Ambiguous variable placement (could go in system or user message)
- History position unclear
- Original prompt meaning might change with restructuring

## Validation Output Format

```
Prompt: [name]
├─ Roles: ✓ all lowercase
├─ Variables: ✓ Mustache format
├─ History: ✓ using placeholder
├─ Structure: ✓ matches analysis
└─ Validation: ✓ PASS
```

If validation fails:
1. Auto-correct if possible
2. If unable to auto-correct, mark as `needs_review`
3. Explain the issue to user clearly
