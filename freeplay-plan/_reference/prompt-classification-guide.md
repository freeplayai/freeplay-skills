# Prompt Classification Guide

Reference for classifying prompts during codebase analysis.

## Complexity Classification

**Simple:**
- Single message
- No variables or simple variables only
- Static content
- Clear structure

**Moderate:**
- Multiple messages
- Variables with clear extraction
- Static tool definitions
- Straightforward conditional logic

**Complex:**
- Dynamic assembly at runtime
- Complex conditional logic
- Runtime-generated content
- Nested loops or complex templates
- Tool definitions built dynamically

## Migration Strategy

**Direct:**
- Can be migrated automatically
- Straightforward variable conversion
- Clear message structure
- No complex logic

**Needs Review:**
- Can be migrated but user should verify
- Variable syntax needs conversion (Jinja → Mustache)
- Multiple message roles need mapping
- Tool schemas need review

**Manual:**
- Too complex for automatic migration
- Requires flattening conditional logic
- Dynamic prompt assembly
- Runtime-generated structures
- Should be flagged for user to handle

## Classification Examples

### Simple Prompts

**Single static system message:**
```yaml
system: "You are a helpful assistant."
```
- Complexity: simple
- Strategy: direct

**System message with basic variable:**
```yaml
system: "You are a {{role}} assistant."
```
- Complexity: simple
- Strategy: direct

### Moderate Prompts

**Multi-turn with variables:**
```yaml
messages:
  - role: system
    content: "You are {{role}}."
  - role: user
    content: "{{user_query}}"
```
- Complexity: moderate
- Strategy: needs_review (verify role mapping)

**With tools:**
```yaml
system: "You have access to these tools: {{tool_list}}"
tools:
  - name: search
    description: "Search the web"
```
- Complexity: moderate
- Strategy: needs_review (verify tool schema format)

### Complex Prompts

**Conditional logic:**
```python
if user_tier == "premium":
    prompt = premium_template
else:
    prompt = basic_template
```
- Complexity: complex
- Strategy: manual (create separate templates)

**Dynamic assembly:**
```python
messages = [{"role": "system", "content": base_system}]
for context_item in context:
    messages.append({"role": "user", "content": context_item})
messages.append({"role": "user", "content": user_query})
```
- Complexity: complex
- Strategy: manual (flatten or keep in code)

**Runtime generation:**
```python
tools = [generate_tool_schema(func) for func in available_functions]
prompt = f"You have {len(tools)} tools: {', '.join(tool.name for tool in tools)}"
```
- Complexity: complex
- Strategy: manual (tools should be defined in code)

## Decision Matrix

| Characteristic | Simple | Moderate | Complex |
|----------------|--------|----------|---------|
| Message count | 1-2 | 2-5 | Variable |
| Variables | 0-2 static | 3-10 clear | Dynamic/nested |
| Logic | None | Basic | Conditional/loops |
| Tools | None/static | Static list | Generated |
| **Typical strategy** | **direct** | **needs_review** | **manual** |

## When to Flag for Manual Migration

Flag a prompt as manual if it has any of:
- Conditional logic that selects different prompts
- Loops that build messages dynamically
- Runtime-generated tool schemas
- Complex nested template logic
- Database queries in prompt assembly
- User tier or permissions-based prompt selection

## Notes

These classifications are guidelines. Use judgment based on the specific codebase and user's comfort level with manual migration.
