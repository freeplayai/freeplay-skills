# Freeplay Observability Patterns

This guide explains how to structure your LLM observability in Freeplay using sessions, traces, agents, and completions.

## Contents
- [The Freeplay Hierarchy](#the-freeplay-hierarchy)
- [1. Sessions](#1-sessions)
  - [What Are Sessions?](#what-are-sessions)
  - [When to Create Sessions](#when-to-create-sessions)
  - [Session Examples](#session-examples)
  - [Session Metadata](#session-metadata)
- [2. Completions](#2-completions)
  - [What Are Completions?](#what-are-completions)
  - [When to Log Completions](#when-to-log-completions)
  - [Completion Metadata](#completion-metadata)
- [3. Traces](#3-traces)
  - [What Are Traces?](#what-are-traces)
  - [Trace Hierarchy](#trace-hierarchy)
  - [Creating Traces](#creating-traces)
  - [Trace Input/Output](#trace-inputoutput)
- [4. Agents (Named Traces)](#4-agents-named-traces)
  - [What Are Agents?](#what-are-agents)
  - [When to Use Agents](#when-to-use-agents)
  - [Creating Agents](#creating-agents)
  - [Agent Naming Best Practices](#agent-naming-best-practices)
- [5. Tool Traces](#5-tool-traces)
  - [What Are Tool Traces?](#what-are-tool-traces)
  - [When to Use Tool Traces](#when-to-use-tool-traces)
  - [Creating Tool Traces](#creating-tool-traces)
- [6. Metadata & Filtering](#6-metadata--filtering)
  - [What Can Be Searched/Filtered?](#what-can-be-searchedfiltered)
  - [Structuring Metadata for Searchability](#structuring-metadata-for-searchability)
  - [Metadata Examples by Use Case](#metadata-examples-by-use-case)
  - [Feedback for Searchability](#feedback-for-searchability)
- [7. Common Integration Patterns](#7-common-integration-patterns)
  - [Pattern 1: Simple Chatbot](#pattern-1-simple-chatbot)
  - [Pattern 2: Simple API Endpoint](#pattern-2-simple-api-endpoint)
  - [Pattern 3: Multi-Step Agent (No Tools)](#pattern-3-multi-step-agent-no-tools)
  - [Pattern 4: Agent with Tools](#pattern-4-agent-with-tools)
  - [Pattern 5: Nested Agents (Complex)](#pattern-5-nested-agents-complex)
  - [Pattern 6: Batch Processing](#pattern-6-batch-processing)
- [8. Decision Guide](#8-decision-guide)
- [9. Testing Your Structure](#9-testing-your-structure)
- [10. Common Mistakes](#10-common-mistakes)
- [11. Summary](#11-summary)

---

## The Freeplay Hierarchy

```
Project
  └── Session (entire user interaction / conversation)
        └── Trace (logical grouping of related LLM calls)
              └── Completion (single LLM API call)
                    └── Tool Trace (optional - tool/function call)
```

**Key Concepts:**
- **Sessions** = Top-level container for an interaction
- **Traces** = Optional logical groupings within a session
- **Agents** = Named traces with enhanced searchability
- **Completions** = Individual LLM calls (prompt → response)
- **Tool Traces** = Special trace type for function/tool calls

---

## 1. Sessions

### What Are Sessions?

**Sessions are the highest-level organizing principle.** They group all completions and traces that make up a customer interaction.

**Scope:** A session can be:
- A single completion (simple use case)
- An entire multi-turn conversation
- A complex agent workflow with dozens of LLM calls
- A multi-hour interaction

**Automatically created:** When you log to Freeplay, a session is created if you don't provide a session ID.

### When to Create Sessions

**Rule:** One session = one logical user interaction

| Your App Type | Session Strategy | Session ID Pattern |
|---------------|------------------|-------------------|
| Chatbot | One per conversation | `user_{id}_conv_{id}` |
| API endpoint | One per request | `str(uuid.uuid4())` |
| Agent workflow | One per user query | `query_{uuid}` |
| Background job | One per job | `job_{id}` |
| Document processing | One per document | `doc_{id}` |
| Multi-turn assistant | One per user session | `user_{id}_session_{ts}` |

### Session Examples

**Chatbot - Reuse across turns:**
```python
# User starts conversation
session_id = f"user_{user_id}_conv_{uuid.uuid4()}"

# Turn 1
completion_1 = log_to_freeplay(session_id=session_id, ...)

# Turn 2 - SAME session
completion_2 = log_to_freeplay(session_id=session_id, ...)

# Turn 3 - SAME session
completion_3 = log_to_freeplay(session_id=session_id, ...)
```

**API Endpoint - New session per request:**
```python
@app.post("/generate")
def generate(request):
    # New session for each request
    session_id = str(uuid.uuid4())
    result = log_to_freeplay(session_id=session_id, ...)
    return result
```

### Session Metadata

Add searchable context to sessions:

```python
session = fp_client.sessions.create(
    custom_metadata={
        "user_id": "user_123",
        "user_tier": "premium",
        "conversation_type": "support",
        "app_version": "2.1.0",
        "environment": "production"
    }
)
```

**Why this matters:** You can filter sessions by any metadata field in Freeplay UI.

---

## 2. Completions

### What Are Completions?

**Completions are atomic units representing a single call to an LLM provider.** They contain:
- Prompt (input messages)
- Response (output)
- Model and provider
- Latency and token usage
- Optional: prompt template linkage
- Optional: evaluation results

### When to Log Completions

**Every time you call an LLM**, log a completion:

```python
# Example: Vanilla OpenAI
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Log to Freeplay
fp_client.recordings.create(
    RecordPayload(
        project_id=project_id,
        session_info=session.session_info,
        all_messages=[...],  # Prompt + response
        prompt_version_info=prompt_info,  # Links to prompt template
    )
)
```

### Completion Metadata

Add evaluation results and custom metadata:

```python
fp_client.recordings.create(
    RecordPayload(
        ...,
        eval_results={
            "is_valid_json": True,
            "sentiment": "positive",
            "contains_pii": False,
            "quality_score": 0.92
        }
    )
)
```

---

## 3. Traces

### What Are Traces?

**Traces are optional mid-level groupings within sessions.** They help structure and visualize logical behavior when multiple LLM calls work together.

**When to use:**
- Multi-step agent workflows (research → reason → answer)
- Complex reasoning chains (plan → execute → verify)
- Parallel LLM calls that contribute to one output
- Multi-agent systems where each trace can represent an agetn

Do not use when:
- Simple single-prompt applications (unnecessary complexity)

### Trace Hierarchy

**Traces can have children:**

```
Session: user_123_xyz
  └── Trace: research_agent
        ├── Completion: web_search_query
        ├── Completion: summarize_results
        └── Trace: fact_verification (child trace)
              ├── Completion: check_fact_1
              └── Completion: check_fact_2
  └── Trace: answer_generation
        └── Completion: final_answer
```

### Creating Traces

**Python (vanilla SDK):**
```python
# Create session
session = fp_client.sessions.create()

# Create parent trace
trace = session.create_trace(
    input="What is the capital of France?",
    agent_name=None,  # Unnamed trace
    custom_metadata={
        "trace_type": "research",
        "complexity": "low"
    }
)

# Log completions within trace
completion = fp_client.recordings.create(
    RecordPayload(
        project_id=project_id,
        session_info=session.session_info,
        parent_id=trace.trace_id,  # Link to trace
        ...
    )
)

# Mark trace complete with output
trace.record_output(
    project_id=project_id,
    output="Paris is the capital of France."
)
```

**LangGraph (automatic):**
```python
from freeplay_langgraph import FreeplayLangGraph

freeplay = FreeplayLangGraph()

# Traces created automatically for each agent invocation
agent = freeplay.create_agent(
    prompt_name="research-assistant",
    tools=[search_web, summarize],
    environment="production"
)

# One trace per invoke()
result = agent.invoke({"messages": [HumanMessage(content="...")]})
```

### Trace Input/Output

Traces capture the beginning and end of a logical process:

```python
# Input: The question/task given to this logical unit
trace = session.create_trace(
    input="Analyze sentiment of: 'This product is amazing!'"
)

# ... LLM calls happen here ...

# Output: The final result of this logical unit
trace.record_output(
    project_id=project_id,
    output="Sentiment: Positive (confidence: 0.95)"
)
```

**Why this matters:** You can see the input→output for each logical step in your agent workflow.

---

## 4. Agents (Named Traces)

### What Are Agents?

**Agents are traces with a name.** The name makes them searchable and filterable in Freeplay.

**Key difference:**
- **Unnamed trace:** Can't filter/search by name in UI
- **Named trace (agent):** Can filter by `agent_name` in UI

### When to Use Agents

Use named traces (agents) when you want to:
- Search/filter by agent type ("show me all research_agent traces")
- Compare performance across different agents
- Track specific agent patterns over time
- Debug specific agent behavior

### Creating Agents

**Python:**
```python
# Named trace = Agent
trace = session.create_trace(
    input="Research the latest AI news",
    agent_name="research_agent",  # This makes it searchable!
    custom_metadata={
        "agent_version": "2.1",
        "max_iterations": 3
    }
)
```

**LangGraph:**
```python
# Agents are named automatically in LangGraph
agent = freeplay.create_agent(
    prompt_name="research-assistant",
    tools=[...],
    environment="production"
)
# Agent name comes from prompt template name
```

### Agent Naming Best Practices

**Good agent names:**
- `research_agent` - Clear purpose
- `fact_checker` - Specific function
- `answer_generator` - Descriptive action
- `query_planner` - Meaningful role

**Bad agent names:**
- `agent_1` - Not descriptive
- `temp` - Not meaningful
- `main` - Too generic

**Why naming matters:** You'll filter by these names in production:
- "Show me all slow `research_agent` traces"
- "Compare `query_planner` v1 vs v2"
- "Find failed `fact_checker` executions"

---

## 5. Tool Traces

### What Are Tool Traces?

**Tool traces are special traces with `kind=tool`.** They represent function/tool calls made by LLMs.

**Visual benefit:** Freeplay UI shows tool traces differently for better workflow visualization.

### When to Use Tool Traces

Use `kind=tool` for:
- Function calls made by LLM (OpenAI functions, Anthropic tools)
- External API calls triggered by agent
- Database queries made during agent execution
- Any discrete "tool use" step

### Creating Tool Traces

**Structure:**
```
Session
  └── Agent Trace: research_agent
        ├── Completion: decide_to_search
        ├── Tool Trace: web_search (kind=tool)  ← Tool call
        ├── Completion: summarize_results
        └── Tool Trace: fetch_details (kind=tool)  ← Another tool
```

**Python example:**
```python
# Parent agent trace
agent_trace = session.create_trace(
    input="Find information about Python",
    agent_name="research_agent"
)

# LLM decides to call a tool
llm_completion = fp_client.recordings.create(...)

# Create tool trace (child of agent trace)
tool_trace = session.create_trace(
    input='{"query": "Python programming", "max_results": 5}',
    agent_name="web_search",  # Tool name
    kind="tool",  # Mark as tool trace
    parent_trace_id=agent_trace.trace_id,  # Nest under agent
    custom_metadata={
        "tool_type": "web_search",
        "api": "google_search"
    }
)

# Execute tool (no LLM call here)
tool_result = execute_web_search(query="Python programming")

# Record tool output
tool_trace.record_output(
    project_id=project_id,
    output=json.dumps(tool_result)
)

# LLM processes tool result
processing_completion = fp_client.recordings.create(...)
```

**LangGraph (automatic):**
```python
# Tool traces created automatically when tools are called
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return "Search results..."

agent = freeplay.create_agent(
    prompt_name="research-assistant",
    tools=[search_web],  # Tools automatically logged as tool traces
    environment="production"
)
```

---

## 6. Metadata & Filtering

### What Can Be Searched/Filtered?

**In Freeplay UI, you can filter by:**

1. **Text Fields** (tokenized phrase matching)
   - Inputs
   - Outputs
   - Evaluation notes

2. **Categorical Fields** (exact match)
   - Model name
   - Provider
   - Environment
   - Prompt template name
   - Review status
   - Agent name

3. **Numeric Fields** (range queries)
   - Cost ($)
   - Latency (ms)
   - Token counts

4. **Key-Value Fields** (two-part matching)
   - Custom metadata (key + value search)
   - Feedback (key + value search)

### Structuring Metadata for Searchability

**Rule:** Break down information into searchable components.

**Bad metadata:**
```python
# Single field with combined info - hard to search
metadata = {
    "user_info": "user_123_premium_usa_2024"
}
```

**Good metadata:**
```python
# Separate fields - easy to filter
metadata = {
    "user_id": "user_123",
    "user_tier": "premium",
    "user_country": "usa",
    "signup_year": "2024"
}
```

**Why this matters:** You can now filter:
- "Show me all premium users"
- "Show me usa users only"
- "Show me 2024 signups"

### Metadata Examples by Use Case

**E-commerce:**
```python
metadata = {
    "customer_id": "cust_789",
    "order_id": "ord_12345",
    "product_category": "electronics",
    "order_value": "1299.99",
    "is_returning_customer": True,
    "support_tier": "gold"
}
```

**Healthcare:**
```python
metadata = {
    "patient_id": "anonymized_abc",
    "department": "cardiology",
    "consultation_type": "followup",
    "urgency_level": "routine",
    "provider_id": "doc_456"
}
```

**SaaS:**
```python
metadata = {
    "tenant_id": "company_xyz",
    "user_role": "admin",
    "feature_accessed": "ai_assistant",
    "subscription_plan": "enterprise",
    "usage_quota_remaining": "750"
}
```

### Feedback for Searchability

Add structured feedback for filtering:

```python
# After user provides feedback
fp_client.customer_feedback.update(
    completion_id=completion_id,
    feedback={
        "freeplay_feedback": "positive",  # Shows as thumbs up in UI
        "feedback_type": "quality",       # Searchable
        "feedback_category": "accurate",   # Searchable
        "user_comment": "Very helpful response!"
    }
)
```

**Filter examples:**
- "Show me all negative feedback"
- "Show me feedback_type=quality"
- "Show me feedback_category=accurate"

---

## 7. Common Integration Patterns

### Pattern 1: Simple Chatbot

**Hierarchy:**
```
Session (one per conversation)
  ├── Completion (turn 1)
  ├── Completion (turn 2)
  └── Completion (turn 3)
```

**No traces needed** - simple back-and-forth.

**Code:**
```python
# Create session once
session_id = f"user_{user_id}_conv_{conv_id}"

# Each turn logs a completion
for user_message in conversation:
    response = call_llm(session_id=session_id, message=user_message)
```

---

### Pattern 2: Simple API Endpoint

**Hierarchy:**
```
Session (one per request)
  └── Completion (single LLM call)
```

**No traces needed** - one-shot generation.

**Code:**
```python
@app.post("/summarize")
def summarize(text: str):
    session_id = str(uuid.uuid4())
    summary = call_llm(session_id=session_id, text=text)
    return {"summary": summary}
```

---

### Pattern 3: Multi-Step Agent (No Tools)

**Hierarchy:**
```
Session (one per query)
  ├── Trace: planner
  │     └── Completion: create_plan
  ├── Trace: researcher
  │     ├── Completion: research_step_1
  │     └── Completion: research_step_2
  └── Trace: answerer
        └── Completion: generate_answer
```

**Use named traces** to organize logical steps.

**Code:**
```python
session_id = f"query_{uuid.uuid4()}"
session = fp_client.sessions.create()

# Step 1: Planning
plan_trace = session.create_trace(
    input=user_query,
    agent_name="planner"
)
plan = call_llm_with_logging(trace=plan_trace, ...)
plan_trace.record_output(project_id=project_id, output=plan)

# Step 2: Research
research_trace = session.create_trace(
    input=plan,
    agent_name="researcher"
)
facts = call_llm_with_logging(trace=research_trace, ...)
research_trace.record_output(project_id=project_id, output=facts)

# Step 3: Answer
answer_trace = session.create_trace(
    input=facts,
    agent_name="answerer"
)
answer = call_llm_with_logging(trace=answer_trace, ...)
answer_trace.record_output(project_id=project_id, output=answer)
```

---

### Pattern 4: Agent with Tools

**Hierarchy:**
```
Session (one per query)
  └── Trace: research_agent
        ├── Completion: decide_action
        ├── Tool Trace: web_search (kind=tool)
        ├── Completion: process_results
        ├── Tool Trace: fetch_details (kind=tool)
        └── Completion: generate_answer
```

**Use tool traces** for function calls.

**Code:**
```python
agent_trace = session.create_trace(
    input=user_query,
    agent_name="research_agent"
)

# LLM decides to search
decision = call_llm_with_logging(trace=agent_trace, ...)

# Execute tool (create tool trace)
tool_trace = session.create_trace(
    input='{"query": "Python", "max_results": 5}',
    agent_name="web_search",
    kind="tool",
    parent_trace_id=agent_trace.trace_id
)
results = execute_tool(...)
tool_trace.record_output(project_id=project_id, output=json.dumps(results))

# LLM processes results
final_answer = call_llm_with_logging(trace=agent_trace, ...)

agent_trace.record_output(project_id=project_id, output=final_answer)
```

---

### Pattern 5: Nested Agents (Complex)

**Hierarchy:**
```
Session (one per query)
  └── Trace: orchestrator
        ├── Completion: analyze_query
        ├── Trace: research_sub_agent (child)
        │     ├── Completion: search
        │     └── Tool Trace: web_search (kind=tool)
        ├── Trace: fact_check_sub_agent (child)
        │     ├── Completion: verify
        │     └── Tool Trace: check_database (kind=tool)
        └── Completion: synthesize_answer
```

**Use nested traces** for sub-agents.

**Code:**
```python
# Main orchestrator
orchestrator = session.create_trace(
    input=user_query,
    agent_name="orchestrator"
)

# Sub-agent 1
research_agent = session.create_trace(
    input="Research: " + user_query,
    agent_name="research_sub_agent",
    parent_trace_id=orchestrator.trace_id  # Nest under orchestrator
)
# ... research logic ...
research_agent.record_output(...)

# Sub-agent 2
fact_checker = session.create_trace(
    input="Verify: " + research_output,
    agent_name="fact_check_sub_agent",
    parent_trace_id=orchestrator.trace_id  # Nest under orchestrator
)
# ... fact check logic ...
fact_checker.record_output(...)

# Orchestrator synthesizes
final = call_llm_with_logging(trace=orchestrator, ...)
orchestrator.record_output(project_id=project_id, output=final)
```

---

### Pattern 6: Batch Processing

**Hierarchy:**
```
Session (one per job)
  ├── Trace: process_doc_1
  │     └── Completion: summarize
  ├── Trace: process_doc_2
  │     └── Completion: summarize
  └── Trace: process_doc_3
        └── Completion: summarize
```

**One session for batch, one trace per item.**

**Code:**
```python
batch_session_id = f"batch_{job_id}"
session = fp_client.sessions.create()

for doc in documents:
    doc_trace = session.create_trace(
        input=doc.text,
        agent_name="document_processor",
        custom_metadata={"document_id": doc.id}
    )

    summary = call_llm_with_logging(trace=doc_trace, ...)
    doc_trace.record_output(project_id=project_id, output=summary)
```

---

## 8. Decision Guide

### Do I Need Sessions?

**Always YES.** Every interaction needs a session.

### Do I Need Traces?

Ask yourself:

**YES, use traces if:**
- Multiple LLM calls contribute to one output
- You have logical "steps" in your workflow
- You want to visualize multi-step reasoning
- You're building an agent with multiple phases

**NO, skip traces if:**
- Single LLM call per session
- Simple chatbot (just back-and-forth)
- API endpoint with one generation

### Do I Need Named Traces (Agents)?

Ask yourself:

**YES, use named traces if:**
- You want to filter by agent type in UI
- You have multiple agent types (research, planning, answering)
- You want to compare agent performance
- You need to debug specific agent behavior

**NO, use unnamed traces if:**
- Only one type of workflow
- Don't need agent-level filtering
- Simple linear flow

### Do I Need Tool Traces?

Ask yourself:

**YES, use `kind=tool` if:**
- LLM calls functions/tools
- You want to visualize tool usage in UI
- You need to debug tool call issues
- You want to track tool performance

**NO, skip tool traces if:**
- No function calling
- No external tool usage

---

## 9. Testing Your Structure

After implementing, verify in Freeplay UI:

### Check Sessions
1. Go to Sessions view
2. Find your session by ID
3. Verify all completions are grouped correctly
4. Check session metadata appears

### Check Traces
1. Click into a session
2. Verify trace hierarchy is correct
3. Check trace input/output displays
4. Verify parent-child relationships

### Check Agents
1. Use agent name filter
2. Verify you can find your named traces
3. Check agent performance metrics

### Check Tool Traces
1. Look for tool traces in workflow view
2. Verify tool input/output is captured
3. Check `kind=tool` displays correctly

### Check Filtering
1. Try filtering by metadata keys
2. Try filtering by agent name
3. Try filtering by feedback
4. Verify all custom fields are searchable

---

## 10. Common Mistakes

### ❌ Mistake 1: Creating New Session Per LLM Call

**Problem:**
```python
# DON'T DO THIS in a chatbot
def handle_message(message):
    session_id = str(uuid.uuid4())  # New session every time!
    return call_llm(session_id=session_id, ...)
```

**Fix:**
```python
# Reuse session for conversation
conversation_sessions = {}

def handle_message(conversation_id, message):
    if conversation_id not in conversation_sessions:
        conversation_sessions[conversation_id] = str(uuid.uuid4())

    session_id = conversation_sessions[conversation_id]
    return call_llm(session_id=session_id, ...)
```

---

### ❌ Mistake 2: Not Using Traces for Multi-Step Agents

**Problem:**
```python
# All completions flat in session - hard to understand flow
session = fp_client.sessions.create()
completion_1 = call_llm(session=session, ...)  # Planning
completion_2 = call_llm(session=session, ...)  # Research
completion_3 = call_llm(session=session, ...)  # Answer
```

**Fix:**
```python
# Use traces to show logical steps
session = fp_client.sessions.create()

plan_trace = session.create_trace(input=query, agent_name="planner")
completion_1 = call_llm(trace=plan_trace, ...)
plan_trace.record_output(...)

research_trace = session.create_trace(input=plan, agent_name="researcher")
completion_2 = call_llm(trace=research_trace, ...)
research_trace.record_output(...)
```

---

### ❌ Mistake 3: Generic Agent Names

**Problem:**
```python
trace = session.create_trace(
    input=query,
    agent_name="agent"  # Not descriptive!
)
```

**Fix:**
```python
trace = session.create_trace(
    input=query,
    agent_name="research_agent"  # Specific and searchable
)
```

---

### ❌ Mistake 4: Monolithic Metadata

**Problem:**
```python
metadata = {
    "info": "user_123_premium_usa_electronics_1299"  # Can't search parts
}
```

**Fix:**
```python
metadata = {
    "user_id": "user_123",
    "tier": "premium",
    "country": "usa",
    "category": "electronics",
    "order_value": "1299"
}
```

---

### ❌ Mistake 5: Forgetting Tool Traces

**Problem:**
```python
# Tool call not logged - can't debug or visualize
result = execute_tool(query)
```

**Fix:**
```python
# Log tool call as tool trace
tool_trace = session.create_trace(
    input=tool_input,
    agent_name="web_search",
    kind="tool",
    parent_trace_id=parent_trace.trace_id
)
result = execute_tool(query)
tool_trace.record_output(project_id=project_id, output=result)
```

---

## 11. Summary

### Hierarchy Quick Reference

```
Session: user_123_conv_456
  ├── Trace: research_agent (agent_name="research_agent")
  │     ├── Completion: plan_research
  │     ├── Tool Trace: web_search (kind=tool)
  │     └── Completion: synthesize_results
  │
  ├── Trace: fact_checker (agent_name="fact_checker")
  │     ├── Completion: verify_claims
  │     └── Tool Trace: check_database (kind=tool)
  │
  └── Trace: answer_generator (agent_name="answer_generator")
        └── Completion: final_answer
```

### When to Use What

| Level | Use When | Searchable By |
|-------|----------|---------------|
| **Session** | Every interaction | Session ID, metadata |
| **Completion** | Every LLM call | Model, template, latency, cost |
| **Trace** | Multi-step logic | Input/output, metadata |
| **Agent (named trace)** | Want to filter by agent type | Agent name |
| **Tool Trace** | Function/tool calls | Tool name, input/output |

### Key Principles

1. **Sessions = user interactions** (always use)
2. **Traces = logical groupings** (use for multi-step)
3. **Agents = named traces** (use for searchability)
4. **Tool traces = function calls** (use for visualization)
5. **Metadata = searchability** (structure for filtering)

### Resources

- **Sessions/Traces/Completions:** https://docs.freeplay.ai/core-concepts/observability/sessions-traces-and-completions
- **UI Filters:** https://docs.freeplay.ai/core-concepts/observability/ui-filters
- **LangGraph Integration:** See `langgraph-complete.md`

---

**Remember:** Structure your observability for how you'll search and debug in production. Good naming and metadata now = easy troubleshooting later.
