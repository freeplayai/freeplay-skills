# Migration Preview Examples

Examples of how to display migration previews to users. Adapt based on actual prompts found.

## Simplified Format (Quick Overview)

```
MIGRATION PREVIEW
═══════════════════════════════════════════════════════════════

✓ main_system_prompt - Variable conversion
⚠ chat_template - Needs review: history handling
✓ tool_prompt - Schema extracted

Approve all? [y/n/edit]
```

## Detailed Format — Call-Site Variables

```
═══════════════════════════════════════════════════════════════
Prompt: code_reviewer
Source: agents/reviewer.py

CALL-SITE VARIABLES DETECTED:
  Found at call sites: language, user_code
  Converting to template variables

FREEPLAY STRUCTURE:
template_messages:
  - role: "system"
    content: "You are a helpful coding assistant."
  - role: "user"
    content: "Review this {{language}} code:\n{{user_code}}"  ← CONVERTED

Variables: ["language", "user_code"]
Transformations:
  - Detected variables at call site (line 45 in agent.py)
  - Converted f-string to template variables
═══════════════════════════════════════════════════════════════
```

## Detailed Format — Static Prompt

```
═══════════════════════════════════════════════════════════════
Prompt: base_system
Source: config/system.txt

FREEPLAY STRUCTURE:
template_messages:
  - role: "system"
    content: "You are a helpful assistant. Always be concise."

Variables: [] (confirmed static system prompt)

Note: User confirmed this is a static configuration prompt with no variables
═══════════════════════════════════════════════════════════════
```

## Detailed Format — History + Tools

```
═══════════════════════════════════════════════════════════════
Prompt: chat_with_tools
Source: agents/chat.py

FREEPLAY STRUCTURE:
template_messages:
  - role: "system"
    content: "You are a helpful assistant with access to tools."
  - kind: "history"
  - role: "user"
    content: "{{user_message}}"

Variables: ["user_message"]
Tool Schema: 3 tools extracted to tool_schema parameter
History: Using {"kind": "history"} placeholder

Transformations:
  - History loop replaced with placeholder
  - Tool definitions extracted to tool_schema
  - User message variable converted from f-string
═══════════════════════════════════════════════════════════════
```

## Per-Prompt Detail

For each prompt preview, include:
- Detected pattern (from decision tree)
- Mapping decision (why this structure)
- Validation status (pass / needs review / failed)
- Original source location
- Freeplay API call with all parameters
- Variables detected
- Transformations applied
