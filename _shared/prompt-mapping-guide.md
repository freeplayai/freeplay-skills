# Prompt Structure Mapping Guide

Comprehensive guide for analyzing prompts and mapping them to Freeplay's structure. Use this during both the **analysis phase** (freeplay-plan) and **migration phase** (prompt-migration).

---

## Table of Contents

### Getting Started
1. [Overview](#overview) - Key principles and when to use this guide
2. [Freeplay API Structure](#freeplay-api-structure) - Required fields and data structure

### Analysis Phase (Planning)
3. [Content Analysis Workflow](#content-analysis-workflow) - How to analyze prompts during planning
4. [Variable Detection Patterns](#variable-detection-patterns) - Finding all variables, not just obvious ones
5. [Role Inference Heuristics](#role-inference-heuristics) - Determining message roles from content

### Migration Phase (Implementation)
6. [Decision Tree: Structure Detection](#decision-tree-structure-detection--mapping) - Pattern matching for all prompt types
7. [Single String Splitting Logic](#single-string-splitting-logic) - When and how to split messages
8. [Before/After Examples](#beforeafter-examples) - Real conversion examples

### Validation & Quality
9. [Validation Checklist](#validation-checklist) - Pre-migration verification
10. [Common Mistakes to Avoid](#common-mistakes-to-avoid) - Pitfalls and how to avoid them
11. [When to Flag for User Review](#when-to-flag-for-user-review) - Escalation criteria

---

## Quick Start (Most Common Cases)

Most prompts fall into one of two patterns. Handle these first, then consult the full Decision Tree for complex cases.

**Pattern A — Single string with variables (most common):**
```
Input:  "You are a helpful assistant. Answer this: {question}"
Output:
  - role: "system" / content: "You are a helpful assistant."
  - role: "user" / content: "{{question}}"
```
Split at the user-input variable. Instructions go in system message, user input goes in user message.

**Pattern B — Pre-structured messages:**
```
Input:  [{"role": "system", "content": "..."}, {"role": "user", "content": "{query}"}]
Output: Normalize roles to lowercase, convert variables to Mustache. Keep existing structure.
```

For complex cases (history loops, tool schemas, output schemas), read the full Decision Tree below.

---

## Overview

This guide helps determine the optimal Freeplay message structure for any prompt. Use the decision tree below to analyze prompt content and structure, then apply appropriate transformations.

**Key principle:** Analyze content intelligently. Don't rigidly map "single string = system message". Consider structure, variables, usage patterns, and intent.

**Two-phase approach:**
- **Analysis phase** (freeplay-plan): Use this guide to deeply analyze prompts, detect variables, infer message structure, and document findings in `analysis.json`
- **Migration phase** (prompt-migration): Use this guide to transform analyzed prompts into Freeplay's API format

---

## Freeplay API Structure

When creating prompts in Freeplay via the `create_prompt_version_and_deploy` MCP tool:

**Required Fields:**
- `template_name`: Unique identifier for the prompt template
- `template_messages`: Array of message objects (see structure below)
- `model`: Model name (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
- `provider`: Provider name (e.g., "openai", "anthropic")
- `environments`: Array of deployment targets (e.g., ["staging"], ["production"])

**Optional Fields:**
- `version_name`: Short label for this version (max 30 chars)
- `version_description`: Detailed description (max 200 chars)
- `llm_parameters`: Object with model settings (temperature, max_tokens, top_p, etc.)
- `tool_schema`: Array of tool/function definitions (OpenAI format)
- `output_schema`: Structured output schema (JSON Schema format)

**Message Structure:**

Messages are objects with:
- `role`: Must be lowercase - `"system"`, `"user"`, or `"assistant"`
- `content`: The message text (can contain Mustache variables)

Special case for conversation history:
- `{"kind": "history"}` - Placeholder for dynamic history (NOT a variable)

**Variable Syntax Requirements:**
- Mustache format only: `{{variable_name}}`
- No spaces inside braces: `{{var}}` ✓, `{{ var }}` ✗
- Variable names must be valid identifiers (alphanumeric + underscore)
- See `convert-to-mustache.md` for conversion details

**Critical Rules:**
1. Roles MUST be lowercase ("System" will fail API validation)
2. History is a placeholder, NOT a template variable
3. Tools and output schemas are separate parameters, NOT in message content
4. All logic/filtering must be done in code before passing to template

---

## Content Analysis Workflow

**Use this section during the ANALYSIS PHASE (freeplay-plan) to deeply analyze each prompt.**

### Step 1: Read the Full Prompt Content AND Its Usage

**Critical:** Don't just analyze the prompt definition - find where and how it's **called**.

Variables and structure are often only visible at the call site:

```python
# Prompt definition (looks simple)
SYSTEM_PROMPT = "You are a helpful assistant."

# But the call site reveals the real structure
def chat(user_query: str, context: str):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Context: {context}"},  # Hidden variable!
            {"role": "user", "content": user_query}                # Hidden variable!
        ]
    )
```

**What to examine:**
1. **Prompt definition** - The template/string itself
2. **Call site(s)** - Where the prompt is used (functions, routes, handlers)
3. **Variable injection** - How data is passed in (`.format()`, f-strings, function args)
4. **Message assembly** - How messages are built around the prompt
5. **Dynamic content** - Conditionals, loops, or logic at call time

**Search patterns to find call sites:**
- Function names that use the prompt variable
- LLM client calls: `.create()`, `.generate()`, `.chat()`, `.complete()`
- Imports of the prompt file
- References to prompt variable names (use Grep)

### Step 2: Identify ALL Variables (Definition + Call Sites)

**Look in TWO places:**
1. **Prompt definition** - Variables in the template itself
2. **Call sites** - Variables passed when the prompt is used

**Variable syntax in definitions:**
- f-strings: `f"{variable}"`, `f"{obj.field}"`, `{variable}`, `{variable:format}`
- Jinja2: `{{ variable }}`, `{{variable}}`, `{% for x in y %}`
- Template literals: `` `${variable}` ``
- Mustache: `{{variable}}`
- Format strings: `"Hello {name}".format(name=x)`

**Variables at call sites (often hidden):**

```python
# Example 1: Variables injected at call time
prompt_template = "You are a coding assistant."  # Looks static!

def generate_response(user_code: str, language: str):
    messages = [
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Review this {language} code:\n{user_code}"}
    ]
    # Variables: user_code, language (NOT in prompt definition!)
```

```python
# Example 2: Dynamic message construction
BASE_PROMPT = "Analyze the following:"  # Looks simple!

def analyze(text: str, context: Optional[str] = None):
    messages = [{"role": "system", "content": "You are an analyst."}]
    if context:
        messages.append({"role": "system", "content": f"Context: {context}"})
    messages.append({"role": "user", "content": f"{BASE_PROMPT}\n{text}"})
    # Variables: text, context (conditional!) - NOT in BASE_PROMPT definition
```

```python
# Example 3: Function parameters become variables
def get_prompt(user_name: str, user_tier: str, query: str):
    return [
        {"role": "system", "content": f"Assistant for {user_tier} user {user_name}"},
        {"role": "user", "content": query}
    ]
    # Variables: user_name, user_tier, query - all from function signature!
```

**How to find call-site variables:**
1. Search for the prompt variable name throughout the codebase
2. Find all functions that use the prompt
3. Examine function parameters - they often become variables
4. Look for string interpolation around the prompt (`f"{prompt}\n{var}"`)
5. Check for message arrays being built dynamically

**Don't just capture what's obvious - analyze what each variable represents:**

```python
# Example prompt analysis
prompt = """
You are a helpful assistant for {company_name}.
Answer this question: {user_question}
Context: {background_info}
"""

# WRONG analysis (surface-level):
variables = ["company_name", "user_question", "background_info"]

# RIGHT analysis (deep):
variables_analysis = {
    "company_name": {
        "name": "company_name",
        "type": "system_context",  # Not user input
        "likely_role": "system"     # Belongs in system message
    },
    "user_question": {
        "name": "user_question",
        "type": "user_input",       # Direct user query
        "likely_role": "user"       # Belongs in user message
    },
    "background_info": {
        "name": "background_info",
        "type": "system_context",   # Contextual information
        "likely_role": "system"     # Belongs in system message
    }
}
```

### Step 3: Classify Variables by Purpose

**User input variables** (should go in user message):
- `query`, `question`, `user_query`, `user_question`, `user_input`
- `text`, `content`, `message`, `user_message`, `prompt`
- `request`, `command`, `instruction`

**System/context variables** (should go in system message):
- `context`, `background`, `knowledge`, `information`
- `rules`, `constraints`, `guidelines`, `instructions`
- `persona`, `role`, `character`, `company_name`
- `tools`, `capabilities`, `functions`, `available_tools`

**Conditional/dynamic variables** (may affect structure):
- `history`, `messages`, `conversation`
- `examples`, `few_shot`, `demonstrations`
- Boolean flags that control message inclusion

### Step 4: Analyze Content Structure

For single-string prompts, look for:
- **Section boundaries**: Line breaks, headers, "Instructions:", "Example:", etc.
- **User input indicators**: "Answer:", "Analyze:", "Translate:", followed by variable
- **Examples**: Few-shot demonstrations that should become user/assistant pairs
- **Instructions vs. input**: Clear separation between system instructions and user query

For pre-structured prompts, verify:
- Are roles correct and consistent?
- Are variables in the right messages?
- Does history need special handling?

### Step 5: Detect Special Patterns

**History loops** - Look for:
- `{% for msg in history %}`, `for message in conversation`
- `.map()` or `.forEach()` over message arrays
- Variable names like `history`, `messages`, `conversation_history`
- **Action**: Flag this as needing `{"kind": "history"}` placeholder

**Tool definitions** - Look for:
- Separate `tools=` or `functions=` parameters
- Tool schema objects with `name`, `description`, `parameters`
- **Action**: Flag for extraction to `tool_schema` parameter

**Structured output** - Look for:
- `response_format`, `output_schema`, Pydantic models
- JSON schema definitions
- **Action**: Flag for extraction to `output_schema` parameter

### Step 6: Document Proposed Structure

Based on analysis, document the proposed message structure in `analysis.json`:

```json
{
  "id": "customer_support_prompt",
  "source": {"file": "prompts/support.py", "lines": "45-52"},

  "content_preview": "You are a customer support agent for {{company}}...",

  "structure": {
    "format": "single_string",
    "proposed_split": true,
    "proposed_messages": [
      {
        "role": "system",
        "content_summary": "Instructions and company context",
        "variables": ["company", "agent_name", "knowledge_base"]
      },
      {
        "role": "user",
        "content_summary": "Customer question",
        "variables": ["customer_question"]
      }
    ]
  },

  "variables": {
    "detected": ["company", "agent_name", "knowledge_base", "customer_question"],
    "user_input_vars": ["customer_question"],
    "system_context_vars": ["company", "agent_name", "knowledge_base"],
    "syntax": "fstring"
  },

  "migration": {
    "complexity": "moderate",
    "strategy": "needs_review",
    "notes": "Single string should split into system + user. Variables clearly separated by purpose."
  }
}
```

**This deep analysis ensures the migration phase will correctly structure the prompt with proper variable placement.**

---

## Decision Tree: Structure Detection & Mapping

Use this tree to determine the optimal structure for any prompt:

### Pattern 1: Single String Prompt

**Detection criteria:**
- Prompt is a single text block (string, not pre-structured messages)
- May contain variables but no explicit role markers

**Mapping logic - Analyze content structure:**

**1a) Pure instructions (no variables in prompt definition)**
- Content describes assistant behavior, constraints, context
- No explicit variables visible in prompt definition
- **IMPORTANT: Analyze call sites to find variables or additional messages**
- **RECOMMENDED: Prompts benefit from variables for dynamic usage**

**Detection strategy:**
1. Check prompt definition for variables ({{var}})
2. Analyze call sites where prompt is used
3. Look for:
   - Variables in surrounding code that could be converted (f-strings, concatenation)
   - Additional messages added at call time (user messages, context)
   - Dynamic content that changes between invocations

**Example - detecting variables at call site:**
```
Prompt definition:
  "You are a helpful coding assistant. Always explain your reasoning step-by-step."

Call site reveals additional messages:
  messages = [
      {"role": "system", "content": PROMPT},
      {"role": "user", "content": f"Review this {language} code:\n{user_code}"}
  ]

Output (with discovered variables from call site):
  template_messages:
    - role: "system"
      content: "You are a helpful coding assistant. Always explain your reasoning step-by-step."
    - role: "user"
      content: "Review this {{language}} code:\n{{user_code}}"

Variables detected: language, user_code
```

**When no variables found at definition or call site:**

Legitimate cases:
- Pure system instructions (rarely change)
- Configuration prompts
- Base personas without dynamic content

**BUT RECOMMENDED to add variable:**
```
Input (static):
  "You are a helpful assistant."

Recommended output (with suggested variable):
  template_messages:
    - role: "system"
      content: "You are a helpful assistant."
    - role: "user"
      content: "{{user_input}}"  ← SUGGESTED

Rationale: Variables enable dynamic prompts, better Freeplay usage
Status: RECOMMENDED (not enforced)
```

**1b) Contains user input variables**
- Has variables indicating user queries: {{query}}, {{question}}, {{user_input}}, {{text}}, {{message}}
- May also have instruction preamble
- **→ Split into system + user messages**

**Example:**
```
Input:
  "You are a helpful assistant. Answer this question: {{user_question}}"

Output:
  template_messages:
    - role: "system"
      content: "You are a helpful assistant."
    - role: "user"
      content: "{{user_question}}"
```

**1c) Multiple logical sections**
- Contains distinct sections (instructions, examples, user input)
- Look for section markers: "Instructions:", "Example:", "User:", line breaks between sections
- **→ Split into appropriate roles (system, user, assistant for examples)**

**Example:**
```
Input:
  "You are a sentiment analyzer.\n\nExample: 'I love this!' → positive\n\nAnalyze: {{text}}"

Output:
  template_messages:
    - role: "system"
      content: "You are a sentiment analyzer."
    - role: "user"
      content: "I love this!"
    - role: "assistant"
      content: "positive"
    - role: "user"
      content: "{{text}}"
```

**1d) Ambiguous structure**
- Unclear whether to split or keep as single message
- Complex logic or unconventional format
- **→ Flag for user review with proposed structure**

---

### Pattern 2: Pre-Structured Messages

**Detection criteria:**
- Already has message list with roles
- May need role normalization or variable conversion

**Mapping logic:**
- Preserve existing structure and message order
- Normalize roles to lowercase: "System" → "system"
- Convert variable syntax (Jinja, f-strings, etc. → Mustache)
- Keep assistant messages for few-shot examples

**Example:**
```
Input:
  messages:
    - role: System
      content: "You are helpful."
    - role: User
      content: "{user_input}"

Output:
  template_messages:
    - role: "system"
      content: "You are helpful."
    - role: "user"
      content: "{{user_input}}"
```

---

### Pattern 3: Conversation History

**Detection criteria:**
- Contains loops iterating over message history
- Keywords: `for message in history`, `{% for msg in messages %}`, `history.forEach`
- May have Jinja loops, Python list comprehension, or programmatic iteration

**Mapping logic:**
- Replace loop with `{"kind": "history"}` placeholder
- Position history placeholder where loop occurred in message sequence
- Preserve surrounding messages (system before, user after)
- Note: History is passed as separate runtime parameter, NOT a template variable

**Example:**
```
Input:
  {% for msg in conversation_history %}
  - role: {{ msg.role }}
    content: {{ msg.content }}
  {% endfor %}
  - role: user
    content: {{ user_query }}

Output:
  template_messages:
    - kind: "history"
    - role: "user"
      content: "{{user_query}}"

  Note: At runtime, pass history separately:
    {"user_query": "...", "history": [{"role": "...", "content": "..."}]}
```

**Common history patterns:**
- Jinja: `{% for msg in history %}`
- Python: `[{"role": m.role, "content": m.content} for m in history]`
- JavaScript: `history.map(m => ({role: m.role, content: m.content}))`

---

### Pattern 4: Tool-Using Prompts

**Detection criteria:**
- Tool/function definitions present alongside prompt
- OpenAI format: `tools=[{...}]` or `functions=[{...}]`
- Anthropic format: `tools=[{...}]`
- LangChain: Tool classes or structured tool schemas

**Mapping logic:**
- Extract tool definitions to `tool_schema` parameter (separate from messages)
- Convert prompt to standard message structure
- Preserve tool-related variables in prompt ({{tool_count}}, {{available_tools}})
- Normalize tool schemas to OpenAI format

**Example:**
```
Input:
  prompt: "You have access to these tools: {{tools_list}}"
  tools: [
    {
      "type": "function",
      "function": {
        "name": "search",
        "description": "Search the web",
        "parameters": {...}
      }
    }
  ]

Output:
  template_messages:
    - role: "system"
      content: "You have access to these tools: {{tools_list}}"
  tool_schema:
    - type: "function"
      function:
        name: "search"
        description: "Search the web"
        parameters: {...}
```

---

### Pattern 5: Structured Output

**Detection criteria:**
- Response format or output schema defined
- OpenAI: `response_format={"type": "json_schema", "schema": {...}}`
- Anthropic: Tool use for structured output
- Pydantic models or TypeScript interfaces defining expected output

**Mapping logic:**
- Extract schema to `output_schema` parameter
- Convert prompt to standard message structure
- For OpenAI: Include `strict: true` in schema if using strict mode
- Preserve output-related instructions in prompt

**Example:**
```
Input:
  prompt: "Extract entities from: {{text}}"
  response_format: ResponseFormat(
    type="json_object",
    schema={
      "type": "object",
      "properties": {
        "entities": {"type": "array", "items": {"type": "string"}}
      }
    }
  )

Output:
  template_messages:
    - role: "system"
      content: "You are a data extraction assistant."
    - role: "user"
      content: "Extract entities from: {{text}}"
  output_schema:
    type: "object"
    properties:
      entities:
        type: "array"
        items:
          type: "string"
    required: ["entities"]
```

---

### Pattern 6: Complex/Ambiguous

**Detection criteria:**
- Doesn't fit other patterns clearly
- Multiple features combined (history + tools + structured output)
- Custom or unconventional structure

**Mapping logic:**
- Analyze components separately
- Propose structure based on closest pattern match
- **→ Always flag for user review with explanation**
- Provide reasoning for proposed mapping

**Example:**
```
Detected: Single string with both instructions and user input variable,
          plus tool definitions and history loop

Proposed:
  template_messages:
    - role: "system"
      content: "[instructions]"
    - kind: "history"
    - role: "user"
      content: "{{user_query}}"
  tool_schema: [...]

Needs Review: Complex structure combining multiple patterns.
              Please verify message flow is correct.
```

---

## Role Inference Heuristics

When roles aren't explicit (e.g., single string prompts), use these content cues:

### System Role Indicators:
- "You are..." statements
- Instructions, rules, constraints
- Context, background information
- Personality, tone guidance
- Tool descriptions, capabilities
- Few-shot example explanations

**Examples:**
- "You are a helpful assistant specialized in Python."
- "Always respond in JSON format."
- "Context: You're helping with customer support."

### User Role Indicators:
- Questions or requests
- Variables containing user input: {{query}}, {{question}}, {{user_input}}, {{message}}, {{text}}
- Imperative commands: "Analyze...", "Summarize...", "Translate..."
- Content clearly from end-user perspective

**Examples:**
- "What is {{topic}}?"
- "{{user_question}}"
- "Analyze this text: {{text}}"

### Assistant Role Indicators:
- Example responses in few-shot prompts
- Demonstration outputs
- Response templates
- Usually paired with preceding user message

**Examples:**
- (After user: "Hello") → "Hi! How can I help you today?"
- (After user: "Classify: I love this!") → "Sentiment: positive"

---

## Single String Splitting Logic

When to split a single string into multiple messages vs. keep as one:

### Keep as Single System Message:
- Pure instructions with no user variables
- Configuration, rules, context only
- No clear user input component

**Example:**
```
"You are a coding assistant. Follow PEP 8. Explain your changes."
→ Single system message
```

### Split into System + User:
- Has user input variables ({{query}}, {{question}}, etc.)
- Clear separation between instructions and user input
- Instructions preamble followed by user-facing query

**Example:**
```
"You are a translator. Translate this to French: {{text}}"
→ System: "You are a translator."
→ User: "Translate this to French: {{text}}"
```

### Split into Multiple Messages:
- Contains few-shot examples (user/assistant pairs)
- Multiple logical sections with different purposes
- Section markers or formatting indicating structure

**Example:**
```
"You classify sentiment.\nUser: I love it!\nAssistant: positive\nUser: {{text}}"
→ System: "You classify sentiment."
→ User: "I love it!"
→ Assistant: "positive"
→ User: "{{text}}"
```

### When Uncertain:
- Default to preserving user's original structure when possible
- If single string is ambiguous, propose split with explanation
- Flag for user review rather than guessing

---

## Variable Detection Patterns

Variables indicating user input (suggests user message needed):

**Common user input variables:**
- {{query}}, {{question}}, {{user_query}}, {{user_question}}
- {{input}}, {{user_input}}, {{message}}, {{user_message}}
- {{text}}, {{content}}, {{prompt}}
- {{request}}, {{command}}

**Context/configuration variables (can stay in system):**
- {{context}}, {{background}}, {{knowledge}}
- {{rules}}, {{constraints}}, {{guidelines}}
- {{persona}}, {{role}}, {{character}}
- {{tools}}, {{capabilities}}, {{functions}}

**Example:**
```
"You are {{persona}}. Answer: {{user_question}}"
                 ↓                    ↓
          (system variable)    (user variable → split needed)
```

---

## Variables: Recommended Best Practice

**RECOMMENDATION:** Most prompts benefit from having at least one variable.

**Why variables are beneficial:**
- Enable dynamic prompt adaptation to different inputs
- Maximize value of Freeplay's version control and A/B testing
- Allow prompt reuse across different contexts
- Make prompts more maintainable and testable

**When variables may not be needed:**
- Pure system instructions that never change
- Static configuration prompts
- Base personality definitions without input-specific content

**Detection checklist:**
1. Check prompt definition for {{variables}}
2. Analyze call sites for:
   - f-strings or concatenation that could become variables
   - Additional messages added at runtime
   - Dynamic content in surrounding code
3. If none found, suggest appropriate variable based on prompt purpose
4. Explain why variable would be beneficial (but don't enforce)

**Common variables by prompt type:**

| Prompt Type | Suggested Variable | Rationale |
|-------------|-------------------|-----------|
| Instructions only | `user_input` or `query` | Capture user intent |
| System prompt | `context` or `background` | Add runtime context |
| Conversational | `user_message` | Enable dialogue |
| Analysis | `text` or `content` | Input to analyze |

**Approach:** Recommend and explain, but respect legitimate static prompts.

---

## Before/After Examples

### Example 1: Single String → Split

**Before:**
```
"You are a helpful assistant. Answer this question: {question}"
```

**After:**
```
template_messages:
  - role: "system"
    content: "You are a helpful assistant."
  - role: "user"
    content: "{{question}}"
```

**Reasoning:** User input variable {{question}} suggests split. Instructions go to system, user query to user message.

---

### Example 2: Pre-Structured → Direct Mapping

**Before:**
```
messages:
  - role: System
    content: "You are helpful."
  - role: User
    content: "{input}"
```

**After:**
```
template_messages:
  - role: "system"
    content: "You are helpful."
  - role: "user"
    content: "{{input}}"
```

**Reasoning:** Already structured. Normalize roles to lowercase, convert variables.

---

### Example 3: History Loop → Placeholder

**Before:**
```
{% for msg in history %}
  role: {{ msg.role }}
  content: {{ msg.content }}
{% endfor %}
role: user
content: {{ query }}
```

**After:**
```
template_messages:
  - kind: "history"
  - role: "user"
    content: "{{query}}"
```

**Reasoning:** Replace history loop with special placeholder. History passed at runtime.

---

### Example 4: Tools → Extract Schema

**Before:**
```
prompt: "Use these tools: {tools}"
tools:
  - name: search
    description: "Search web"
    parameters: {...}
```

**After:**
```
template_messages:
  - role: "system"
    content: "Use these tools: {{tools}}"
tool_schema:
  - type: "function"
    function:
      name: "search"
      description: "Search web"
      parameters: {...}
```

**Reasoning:** Extract tool definitions to separate parameter. Keep tool references in prompt.

---

### Example 5: Structured Output → Extract Schema

**Before:**
```
prompt: "Extract data from {text}"
output_format: {
  "type": "object",
  "properties": {"name": {"type": "string"}}
}
```

**After:**
```
template_messages:
  - role: "system"
    content: "You are a data extraction assistant."
  - role: "user"
    content: "Extract data from {{text}}"
output_schema:
  type: "object"
  properties:
    name:
      type: "string"
  required: ["name"]
```

**Reasoning:** Extract schema to separate parameter. Add system context for clarity.

---

### Example 6: Few-Shot → Multi-Message

**Before:**
```
"Classify sentiment. Example: 'I love this!' → positive. Now: {text}"
```

**After:**
```
template_messages:
  - role: "system"
    content: "Classify sentiment."
  - role: "user"
    content: "I love this!"
  - role: "assistant"
    content: "positive"
  - role: "user"
    content: "{{text}}"
```

**Reasoning:** Convert inline example to proper message structure with user/assistant roles.

---

## Validation Checklist

Before finalizing migration, verify:

### Message Structure:
- [ ] All roles are lowercase ("system", "user", "assistant")
- [ ] At least one message present
- [ ] Messages have both `role` and `content` fields
- [ ] History uses `{"kind": "history"}` not `{{history}}`

### Variable Syntax:
- [ ] All variables use Mustache: `{{var}}`
- [ ] No spaces inside braces: `{{var}}` not `{{ var }}`
- [ ] Variable names are valid identifiers (no spaces, special chars)
- [ ] History is NOT a variable (common mistake)

### Extracted Parameters:
- [ ] Tools moved to `tool_schema` (not in message content)
- [ ] Output schemas moved to `output_schema`
- [ ] Model parameters in `llm_parameters` (temperature, max_tokens, etc.)

### Content Integrity:
- [ ] Instructions preserved (not lost in splitting)
- [ ] User input variables assigned to appropriate messages
- [ ] Few-shot examples maintain user/assistant pairing
- [ ] Original intent and flow maintained

### Edge Cases:
- [ ] Empty messages removed
- [ ] Whitespace normalized (no leading/trailing unless intentional)
- [ ] Special characters escaped if needed
- [ ] Multi-line content properly formatted

---

## Common Mistakes to Avoid

1. **Capitalizing roles**: "System" → "system" (API rejects capitals)
2. **History as variable**: `{{history}}` → `{"kind": "history"}` (special placeholder)
3. **Tools in messages**: Extract to `tool_schema` parameter
4. **Losing instructions**: When splitting, ensure system message gets instructions
5. **Wrong role assignment**: Analyze content intent, don't guess arbitrarily
6. **Over-splitting**: Not every single string needs multiple messages
7. **Variable syntax**: Converting to Mustache but forgetting history placeholder

---

## Cross-References

- **Variable syntax details**: See `convert-to-mustache.md` for comprehensive Mustache conversion rules and examples
- **Freeplay API docs**: [https://docs.freeplay.ai](https://docs.freeplay.ai)

---

## When to Flag for User Review

Always get user confirmation when:

1. **Ambiguous structure**: Multiple valid interpretations possible
2. **Complex combinations**: History + tools + structured output in one prompt
3. **Unconventional formats**: Custom or framework-specific patterns
4. **High-stakes prompts**: Production-critical or sensitive content
5. **Uncertain splitting**: Not clear if single string should split
6. **Missing context**: Can't determine intent from content alone

**How to flag:**
- Propose a structure with clear reasoning
- Explain what's ambiguous and why review is needed
- Offer alternatives if applicable
- Make it easy to approve/reject/modify

---

## Summary

**Decision process:**
1. Identify pattern (single string, pre-structured, history, tools, output, complex)
2. Apply mapping logic for that pattern
3. Use role heuristics if roles unclear
4. Extract tools/schemas to parameters
5. Convert variable syntax to Mustache
6. Validate result against checklist
7. Flag for review if uncertain

**Remember:** The goal is intelligent analysis, not rigid rules. Consider context, intent, and usage when making decisions.
