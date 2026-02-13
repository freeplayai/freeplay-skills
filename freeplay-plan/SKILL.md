---
name: freeplay-plan
description: "Analyze a codebase to map its LLM implementation for Freeplay migration. Examines prompts, model configs, tool use, sessions, and agent patterns. Use when user wants to understand their LLM usage, inventory prompts, plan a migration, audit LLM patterns, or before integrating with Freeplay \u2014 even if they just say 'analyze my code' or 'what LLM stuff do I have'."
---

# /freeplay-plan

Analyze a codebase to understand its LLM usage patterns and create a migration plan for Freeplay onboarding.

## When to Use

Use this skill when the user:
- Needs to understand their existing LLM implementation before migrating to Freeplay
- Wants to inventory all prompts, agents, and LLM interactions across their codebase
- Is planning Freeplay integration and needs to identify migration touchpoints
- Asks to analyze, audit, or map their current LLM usage patterns
- Plan a migration to Freeplay for prompt management

**Important:** This skill performs **read-only analysis** of the codebase. It does NOT:
- Call Freeplay APIs
- Use MCP tools
- Modify code
- Create anything in Freeplay

It only scans files and generates an analysis plan based on best practices. Migration happens in `/prompt-migration` and logging happens in `/record-to-freeplay`.

## Reference Materials

See `_shared/llms.txt` for Freeplay documentation links. For observability concepts, see `../record-to-freeplay/_reference/patterns/freeplay-patterns.md`. When interacting with Freeplay, prefer using the MCP server tools (`mcp__freeplay-mcp-v1__*`) first. For endpoints or operations not covered by MCP tools, see `_shared/FREEPLAY_API_REFERENCE.md` for raw API endpoints and request/response shapes.

### Step 1: Initial Scan

Scan the codebase to identify:

**Prompt Files** - Search for files by extension:
- `.txt`, `.md`, `.yaml`, `.yml`, `.json` in directories named `prompts/`, `templates/`, `system/`
- `.jinja`, `.jinja2`, `.j2`, `.prompt`, `.tmpl`
- Look for prompt-like content in config files

**Prompt Strings in Code** - Search for patterns:
- Variables named `system_prompt`, `prompt`, `instructions`, `system_message`
- Multi-line strings with LLM instruction patterns ("You are", "Your task is", "As an AI")
- f-strings or template literals with prompt content

**LLM Client Usage** - Search for imports:
- `openai` - OpenAI SDK
- `anthropic` - Anthropic SDK
- `langchain`, `langchain_core`, `langchain_openai`, `langchain_anthropic`
- `langgraph` - LangGraph framework
- `google.generativeai`, `google.adk` - Google AI / ADK
- `vercel_ai`, `ai` - Vercel AI SDK
- `litellm` - LiteLLM

**Framework Detection** - Look for:
- LangGraph: `StateGraph`, `MessageGraph`, `@node`, `add_edge`
- LangChain: `ChatPromptTemplate`, `PromptTemplate`, `Chain`
- Google ADK: `Agent(`, `create_agent(`, `google.adk` imports
- Vercel AI SDK: `generateText`, `streamText`, `tool`

See `_reference/framework-detection.md` for additional Grep patterns and detection logic.

**Existing Telemetry** - Search for:
- `opentelemetry` imports
- `langsmith` integration
- Custom logging around LLM calls
- `@trace` decorators

### Step 1.5: Analyze Project Architecture

Beyond finding files, understand the structure and flow:

1. **Entry Points & Flow of LLM Data**
   - Where do LLM requests enter and how is information passed through the system?
   - How does data flow through the application?
   - What is the request-to-response lifecycle?

2. **LLM Interaction Points**
   - Where are LLM calls made?
   - When called, what information, variables, messages, etc. are added before the call?
   - Are they centralized or scattered across code, files, or elsewhere?
   - Is there a client abstraction or direct SDK/API calls?

3. **Data Sources**
   - Where does prompt data come from?
   - How is context assembled?
   - Are there databases, files, or APIs providing data?

4. **State Management**
   - How are LLM messages and history stored/used? Are messages added at call time?
   - What is the best definition of a session (e.g., an entire conversation)?
   - Are there multi-turn or multi-agent patterns?

5. **LLM Design & Use**
   - Is the system agentic, workflow-based, single-prompt, multi-agent, etc.?
   - How do prompts interact? What information is passed between them?
   - How do they get messages and context when calling LLMs?

Document findings in `analysis.json` under an `architecture` section to help understand the system interactions.

### Step 2: Build Prompt Inventory (Deep Analysis)

For each prompt discovered in Step 1, perform deep analysis using the **Content Analysis Workflow** from `../_shared/prompt-mapping-guide.md`.

This goes beyond capturing what's visible in the prompt definition -- you need to trace how each prompt is actually used at call sites to find hidden variables, history loops, and dynamic message construction. Thorough analysis here means correct migrations later.

#### For Each Prompt:

**A) Read the prompt content AND find its usage:**

```python
# 1. Prompt definition
SYSTEM_PROMPT = "You are helpful."  # Looks simple...

# 2. BUT the call site reveals the real structure
def chat_handler(user_query: str, context: str, history: list):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Context: {context}"},  # Hidden variable!
    ]
    for msg in history:  # History loop!
        messages.append(msg)
    messages.append({"role": "user", "content": user_query})
    return client.chat(messages=messages)
    # Variables found: context, user_query, history (NOT visible in prompt definition!)
```

**Search for call sites:**
- Grep for the prompt variable name
- Find LLM client calls: `.create()`, `.chat()`, `.generate()`
- Look at function signatures that use the prompt
- Check for dynamic message construction

**B) Analyze variables deeply:**

Don't just list variables -- **classify them by purpose**:

- **User input vars** (go in user message): `query`, `question`, `user_input`, `text`, `message`, `request`
- **System context vars** (go in system message): `context`, `background`, `company_name`, `persona`, `rules`, `tools_list`
- **Dynamic vars** (special handling): `history`, `conversation`, `examples`, boolean flags

**C) Variable detection process for each prompt:**
1. Check the prompt definition for explicit variables (`{{var}}`, `{var}`, `%s` placeholders)
2. Find all call sites where this prompt is used
3. At each call site, look for:
   - Dynamic string construction (f-strings, concatenation, `.format()`)
   - Messages added at runtime (`messages.append`, history loops)
   - Function parameters that feed into the prompt
4. Combine findings and classify variables by purpose (user input, system context, dynamic)
5. If no variables found anywhere, flag as `needs_user_input` for confirmation

**D) Determine proposed message structure:**

Based on variable classification and content analysis, document the proposed structure. See `_reference/example-analysis.json` for complete examples of how to represent structure, variables, and proposed messages.

**E) Classify complexity and strategy:**

See `_reference/prompt-classification-guide.md` for detailed criteria:
- **Complexity**: simple | moderate | complex (based on variables, logic, structure)
- **Strategy**: direct | needs_review | manual (based on conversion difficulty)

**Complete inventory structure per prompt:**
```json
{
  "id": "chat_handler_prompt",
  "source": {
    "file": "handlers/chat.py",
    "lines": "15-25",
    "type": "inline_code"
  },
  "content_preview": "You are helpful. Context: {context}...",
  "structure": {
    "format": "dynamic_construction",
    "proposed_split": true,
    "proposed_messages": [
      {"role": "system", "content_summary": "Base instructions", "variables": []},
      {"role": "system", "content_summary": "Dynamic context", "variables": ["context"]},
      {"kind": "history"},
      {"role": "user", "content_summary": "User query", "variables": ["user_query"]}
    ]
  },
  "variables": {
    "detected": ["context", "user_query", "history"],
    "user_input_vars": ["user_query"],
    "system_context_vars": ["context"],
    "dynamic_vars": ["history"],
    "syntax": "fstring"
  },
  "has_tools": false,
  "has_history": true,
  "migration": {
    "complexity": "moderate",
    "strategy": "needs_review",
    "notes": "History loop at call site needs conversion to {kind: 'history'} placeholder. Context should be separate system message."
  }
}
```

See `_reference/output-schema.json` for the complete structure.

### Step 2.5: Map to Freeplay Structure

After understanding the project, create an explicit mapping to Freeplay's hierarchy. **Present 2-3 concrete examples from the user's codebase and ask for confirmation.**

**Mapping template:**

```
Your Application          ->  Freeplay Structure
-----------------------------------------------------
[conversation/request ID] ->  Session
[agent workflow/function]  ->  Trace (named: agent_type)
[each LLM API call]       ->  Completion
[tool/function calls]      ->  Tool Trace (kind="tool")
[user_id, tier, context]   ->  Metadata (searchable)
```

Walk through 2-3 concrete examples from the user's code showing exactly how their patterns map.

**Ask user to confirm:** "Does this mapping match your application's structure? Any corrections?"

Add to `analysis.json`:
```json
{
  "freeplay_mapping": {
    "sessions": {
      "pattern": "one_per_conversation",
      "id_source": "conversation_id variable"
    },
    "traces": {
      "needed": true,
      "agents": [{"name": "agent_name", "location": "path/to/file.py", "uses_tools": true}],
      "notes": "Detailed notes and assumptions about the mapping"
    },
    "user_confirmed": true
  }
}
```

### Step 2.7: Analyze Model Configurations

For each prompt, capture the full configuration to support migration:

- **Model**: Which model is used (gpt-4, claude-3-5-sonnet, etc.)
- **Provider**: OpenAI, Anthropic, etc.
- **Parameters**: temperature, max_tokens, top_p, etc.
- **Tool schemas**: Any tool/function definitions
- **Output schemas**: Structured output definitions (Pydantic models, JSON schemas)
- **Loading pattern**: How the prompt is loaded (file read, inline, config, etc.)

See `_reference/example-analysis.json` for complete examples of model config representation.

### Step 3: Detect Framework & Recommend Approach

Build a framework assessment:

```json
{
  "framework": {
    "detected": "langgraph|langchain|vanilla_openai|vanilla_anthropic|vercel|adk|unknown",
    "confidence": "high|medium|low",
    "evidence": ["import statement", "usage pattern"],
    "version": "if detectable",
    "recommended_package": "freeplay-langgraph|@freeplayai/vercel|freeplay|freeplay-python-adk"
  },
  "existing_telemetry": {
    "detected": true,
    "type": "opentelemetry|langsmith|custom|none",
    "evidence": ["import or usage"]
  },
  "llm_providers": ["openai", "anthropic"],
  "recommended_integration": "Description of recommended logging approach"
}
```

**Framework to Package Mapping:**
| Framework | Recommended Package | Integration Type |
|-----------|--------------------|--------------------|
| LangGraph | `freeplay-langgraph` | Auto-instrumented |
| LangChain | `freeplay-langgraph` | Via LangGraph |
| Vercel AI SDK | `@freeplayai/vercel` | OpenTelemetry spans |
| Google ADK | `freeplay-python-adk` | Auto-instrumented (OTel + plugin) |
| Vanilla OpenAI | `freeplay` | Manual wrapper |
| Vanilla Anthropic | `freeplay` | Manual wrapper |

**Detect Observability Patterns:**

While analyzing the codebase, identify patterns that map to Freeplay's hierarchy:

- **Session Patterns**: Look for conversation IDs, user IDs, request IDs
  - `conversation_id`, `user_session`, UUID/GUID per request -> Will map to Freeplay Sessions

- **Agent/Trace Patterns**: Look for multi-step related workflows
  - LangGraph `StateGraph` invocations -> Traces (auto-created)
  - Sequential LLM calls working toward one goal -> Should use Traces
  - Named agent functions -> Should use named Traces (agents)

- **Tool Usage**: Look for function/tool calling
  - OpenAI function calling -> Tool Traces
  - LangChain tools -> Tool Traces (auto-created in LangGraph)
  - External API calls triggered by LLM -> Should use Tool Traces

Include session, agent, and tool patterns in `analysis.json`. See `_reference/example-analysis.json` for complete examples.

**Reference:** See `../record-to-freeplay/_reference/patterns/freeplay-patterns.md` for how these patterns map to Freeplay's observability structure.

### Step 4: Identify Edge Cases

Flag any of these patterns found:

| Pattern | Detection Method | Recommendation |
|---------|------------------|----------------|
| Prompts in multiple formats | Multiple file types found | Normalize to Freeplay format |
| Dynamic prompt assembly | String concatenation, conditionals in prompt code | Flag for manual review |
| Prompts in database | ORM models with prompt fields, DB connection + prompt queries | Out of scope - note for user |
| Monorepo with multiple agents | Multiple LLM client instantiations in different directories | Ask user to select scope |
| Prompts split across files | Imports/includes in prompt files | Consolidate or maintain structure |
| Environment-specific prompts | Different prompts per env | Map to Freeplay environments |

### Step 5: Generate Analysis Report

Create `.freeplay/analysis.json` with the structure provided in `_reference/output-schema.json`.

See `_reference/example-analysis.json` for a complete, realistic example with all fields populated.

### Step 6: Present Plan to User

Display a summary for the user:

```
FREEPLAY MIGRATION PLAN
===============================================

Codebase: /path/to/project
Framework: LangGraph (high confidence)
Existing telemetry: None detected

PROMPTS FOUND: 5
  3 ready for direct migration
  1 needs review (variable syntax conversion)
  1 requires manual migration (dynamic assembly)

PROMPT INVENTORY:
| Name             | Source           | Complexity | Strategy     | Variables      |
|------------------|------------------|------------|--------------|----------------|
| main_system      | prompts/main.yml | simple     | direct       | 0 -> 2 (*)    |
| chat_template    | prompts/chat.j2  | moderate   | needs_review | 3              |
| tool_prompt      | agents/tools.py  | simple     | direct       | 2 (call-site)  |
| dynamic_router   | agents/router.py | complex    | manual       | 1 + conditional |
| fallback_system  | prompts/fb.txt   | simple     | direct       | 0 (?)          |

Variable Detection Notes:
  (*) main_system: No variables in definition, but found 2 at call sites (user_query, context)
  (call-site): Variables found in surrounding code, not in prompt definition
  (?) fallback_system: No variables detected - flagged for user confirmation

RECOMMENDED APPROACH:
  Prompts: Migrate 4 prompts to Freeplay, 1 remains in code
  Logging: Install freeplay-langgraph package (auto-instrumented)
  Variables: Convert Jinja {{var}} to Freeplay Mustache {{var}} syntax

WARNINGS:
  dynamic_router uses conditional logic - will need manual flattening

FREEPLAY STRUCTURE MAPPING:
| Your Application    | Freeplay Structure                |
|---------------------|-----------------------------------|
| [detected pattern]  | Session                           |
| [detected pattern]  | Trace (agent_name from agent type)|
| [detected pattern]  | Completion                        |
| [detected pattern]  | Tool Trace (kind="tool")          |
| [detected pattern]  | Metadata (searchable)             |

WHAT WILL BE LOGGED:
  Sessions (keyed by [detected session pattern])
  Traces (one per [detected agent pattern])
  Completions (each LLM call)
  Tool calls (if detected)
  Metadata (relevant context)
```

Ask for confirmation or clarifying questions before proceeding.

### Step 7: Gather User Input

Ask clarifying questions:

1. **Scope**: "I found prompts in these directories: [list]. Should I include all of them?"

2. **Naming**: "Here are the proposed Freeplay template names. Would you like to change any?"

3. **Variables - detected**: "I detected these variables: [list]. Are there any I missed or misidentified?"

4. **Variables - none found**: For prompts flagged with no variables detected:
   - Is this a static system prompt that never changes?
   - How is user input provided to this prompt?
   - Are there variables missed in the code?
   - If truly static, migrate as-is. Otherwise, ask the user to point to where the variables are used.

5. **Complex prompts**: "This prompt has conditional logic I can't fully migrate: [show code]. Options:
   - Flatten to multiple separate templates
   - Keep in code and reference manually
   - Flag for later manual migration"

6. **Framework confirmation**: "I detected [framework]. Is this correct? This determines the logging integration approach."

Update `.freeplay/analysis.json` with user decisions.

### Step 8: Approval Gate

Before completing, get explicit approval:

"Here's the final migration plan. Ready to proceed to prompt migration?
- Run `/prompt-migration` to migrate prompts to Freeplay
- Run `/freeplay-onboarding` to continue the full onboarding flow

**What happens next:** The migration will transform your prompts to match Freeplay's API structure (with proper message format, variable syntax, tool schemas, etc.) based on the analysis in `analysis.json`."

## State Management

**Creates:**
- `.freeplay/` directory (if not exists)
- `.freeplay/analysis.json` - Full analysis and approved plan

**Reads:**
- Nothing (this is the first phase)

## Error Handling

- If no prompts found: Ask user to point to prompt locations
- If no LLM usage found: Confirm this is the right codebase
- If multiple frameworks detected: Ask user to clarify primary framework
- If codebase is very large: Ask user to specify subdirectories to scan

## Freeplay Concepts to Explain to User

When presenting the plan, briefly explain:

**Prompt Templates:**
- Versioned in Freeplay with full history
- Deployed to environments (staging, production)
- Variables use Mustache syntax: `{{variable}}`

**Observability:** Session -> Trace (optional for agents) -> Completion

Map existing patterns to Freeplay:
- Conversation IDs -> Sessions
- Multi-step workflows -> Traces (optionally named as "agents")
- Individual LLM calls -> Completions

**Integration packages** based on detected framework:
- LangGraph: `freeplay-langgraph` (auto-instrumented)
- Google ADK: `freeplay-python-adk` (auto-instrumented)
- Vercel AI SDK: `@freeplayai/vercel`
- Vanilla SDKs: `freeplay` package

See `../record-to-freeplay/_reference/patterns/freeplay-patterns.md` for complete observability guidance.

## Notes

- This skill does NOT make any changes to the codebase
- This skill does NOT call any Freeplay APIs
- All findings are saved locally for the next phase
- User can re-run this skill to update the analysis
