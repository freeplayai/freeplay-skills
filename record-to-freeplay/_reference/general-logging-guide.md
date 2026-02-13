# Freeplay Logging Integration Guide

The general pattern for logging LLM calls to Freeplay. Use this as the primary reference when generating integration code. Framework-specific files in `integrations/` are supplementary examples.

Freeplay supports Python, JavaScript/TypeScript, and direct API calls.

**Model and model parameters are managed in Freeplay** for all integrations. The model, provider, and parameters (temperature, max_tokens, etc.) are configured in the Freeplay UI as part of the prompt template and fetched at runtime via `get_formatted` / `getFormatted`. Generated code should never hardcode model names or parameters.

## The Core Flow

Every Freeplay integration follows this flow:

```
1. Initialize Freeplay client
2. Create a session (per conversation/interaction)
3. Create a trace (per agent workflow/logical step)
4. Fetch formatted prompt from Freeplay (with variables + history)
5. Call the LLM using prompt data and model parameters from Freeplay
6. Record the completion back to Freeplay
7. Handle tool calls (if any) with tool traces
8. Close the trace with output
9. Optionally record customer feedback
```

## Freeplay Hierarchy

```
Session (entire user interaction / conversation)
  └── Trace (logical grouping: agent workflow, multi-step task)
        ├── Completion (single LLM API call)
        ├── Tool Trace (function/tool call, kind="tool")
        └── Completion (LLM processing tool result)
```

**When to use what:**
- **Session**: Always. One per conversation or user interaction.
- **Trace**: When you have multi-step workflows or agents. Skip for simple single-prompt apps.
- **Tool Trace**: When LLM calls tools/functions. Nested under parent trace.
- **Completion**: Every LLM call. Always.

---

## Python SDK

### Installation

```bash
pip install freeplay
# Plus your LLM provider SDK:
pip install openai    # for OpenAI
pip install anthropic # for Anthropic
```

### Client Setup

```python
import os
from freeplay import Freeplay

fp_client = Freeplay(
    freeplay_api_key=os.environ["FREEPLAY_API_KEY"],
    api_base=os.environ.get("FREEPLAY_API_BASE", "https://app.freeplay.ai/api"),
)

project_id = os.environ["FREEPLAY_PROJECT_ID"]
```

### Helper: Call and Record

A reusable helper that fetches a prompt, calls the LLM, and records to Freeplay:

```python
from freeplay import RecordPayload
from openai import OpenAI

openai_client = OpenAI()

def call_and_record(
    template_name: str,
    project_id: str,
    prompt_vars: dict,
    session,
    environment: str = "latest",
    history: list = None,
    trace=None,
):
    """Fetch prompt from Freeplay, call LLM, record completion. Returns (assistant_message, raw_response)."""
    formatted_prompt = fp_client.prompts.get_formatted(
        project_id=project_id,
        template_name=template_name,
        environment=environment,
        variables=prompt_vars,
        history=history,
    )

    response = openai_client.chat.completions.create(
        model=formatted_prompt.prompt_info.model,
        messages=formatted_prompt.llm_prompt,
        tools=formatted_prompt.tool_schema,
        **formatted_prompt.prompt_info.model_parameters,
    )
    llm_response = response.choices[0].message
    all_messages = formatted_prompt.all_messages(llm_response)

    fp_client.recordings.create(
        RecordPayload(
            project_id=project_id,
            all_messages=all_messages,
            inputs=prompt_vars,
            parent_id=trace.trace_id if trace else None,
            prompt_version_info=formatted_prompt.prompt_info,
            session_info=session.session_info,
        )
    )

    return llm_response, response
```

### Pattern: Agent with Tool Calling Loop

A complete example showing sessions, traces, tool traces, history management, and feedback:

```python
import json
import uuid
from datetime import datetime

def run_agent(question: str, user_id: str = None):
    """Run an agent with tool calling and full Freeplay logging."""
    session = fp_client.sessions.create(
        custom_metadata={
            "user_id": user_id or "anonymous",
            "timestamp": datetime.now().isoformat(),
        },
    )

    trace = session.create_trace(
        input=str(question),
        agent_name="assistant",
        custom_metadata={
            "question_length": len(question),
        },
    )

    history = []
    prompt_vars = {"question": question}
    tool_count = 0
    finished = False

    while not finished and tool_count < 5:
        assistant_msg, response = call_and_record(
            template_name="assistant_prompt",
            project_id=project_id,
            prompt_vars=prompt_vars,
            session=session,
            history=history,
            trace=trace,
        )

        history.append(assistant_msg)

        if response.choices[0].finish_reason == "tool_calls":
            tool_count += 1
            tool_call = response.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            tool_result = execute_tool(tool_call.function.name, args)

            # Tool trace: kind="tool", nested under parent via parent_id
            tool_trace = session.create_trace(
                input=json.dumps(args),
                agent_name=tool_call.function.name,
                kind="tool",
                parent_id=trace.trace_id,
            )
            tool_trace.record_output(
                project_id=project_id,
                output=json.dumps(tool_result),
            )

            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            })

            # Optional: sub-agent trace for processing tool result
            sub_trace = session.create_trace(
                input=f"Process result from: {tool_call.function.name}",
                agent_name="result_processor",
                parent_id=trace.trace_id,
            )

            processed_msg, _ = call_and_record(
                template_name="process_result",
                project_id=project_id,
                prompt_vars={
                    "question": question,
                    "tool_result": json.dumps(tool_result),
                },
                session=session,
                history=None,  # Fresh context for sub-agent
                trace=sub_trace,
            )

            sub_trace.record_output(
                project_id=project_id,
                output=str(processed_msg.content),
            )

            history.append(processed_msg)
        else:
            finished = True

    trace.record_output(
        project_id=project_id,
        output=str(assistant_msg.content),
    )

    return assistant_msg.content, trace


def execute_tool(name: str, args: dict):
    """Replace with your actual tool implementations."""
    return {"result": f"Executed {name} with {args}"}
```

### Pattern: Recording Customer Feedback

```python
def record_feedback(trace, feedback_rating: str, feedback_reason: str = None):
    """Record customer feedback ("positive"/"negative") on a trace."""
    feedback = {
        "freeplay_feedback": feedback_rating,
    }
    if feedback_reason:
        feedback["feedback_reason"] = feedback_reason

    fp_client.customer_feedback.update_trace(
        project_id=project_id,
        trace_id=trace.trace_id,
        feedback=feedback,
    )
```

### Pattern: Simple Chatbot (No Traces)

For simple back-and-forth chat, you can skip traces:

```python
def chat(user_message: str, conversation_history: list, session):
    """Simple chatbot without traces."""
    response_msg, _ = call_and_record(
        template_name="chatbot",
        project_id=project_id,
        prompt_vars={"user_message": user_message},
        session=session,
        history=conversation_history,
    )
    return response_msg
```

### Pattern: Client Evaluations

Add programmatic scores when recording:

```python
fp_client.recordings.create(
    RecordPayload(
        project_id=project_id,
        all_messages=all_messages,
        inputs=prompt_vars,
        session_info=session.session_info,
        prompt_version_info=formatted_prompt.prompt_info,
        eval_results={
            "is_valid_json": True,
            "sentiment_score": 0.85,
            "contains_pii": False,
        },
    )
)
```

---

## JavaScript/TypeScript SDK

### Installation

```bash
npm install freeplay
# Plus your LLM provider SDK:
npm install openai
```

### Client Setup

```typescript
import Freeplay from "freeplay";
import OpenAI from "openai";

const fpClient = new Freeplay({
  freeplayApiKey: process.env.FREEPLAY_API_KEY,
  apiBase: process.env.FREEPLAY_API_BASE || "https://app.freeplay.ai/api",
});

const projectId = process.env.FREEPLAY_PROJECT_ID;
const openai = new OpenAI();
```

### Helper: Call and Record

```typescript
async function callAndRecord(
  templateName: string,
  promptVars: Record<string, string>,
  session: any,
  options?: {
    environment?: string;
    history?: Array<{ role: string; content: string }>;
    trace?: any;
  }
) {
  const { environment = "latest", history, trace } = options || {};

  const formattedPrompt = await fpClient.prompts.getFormatted({
    projectId,
    templateName,
    environment,
    variables: promptVars,
    history,
  });

  const response = await openai.chat.completions.create({
    model: formattedPrompt.promptInfo.model,
    messages: formattedPrompt.llmPrompt,
    tools: formattedPrompt.toolSchema,
    ...formattedPrompt.promptInfo.modelParameters,
  });

  const assistantMessage = response.choices[0].message;
  const allMessages = formattedPrompt.allMessages(assistantMessage);

  await fpClient.recordings.create({
    projectId,
    allMessages,
    inputs: promptVars,
    parentId: trace?.traceId,
    promptVersionInfo: formattedPrompt.promptInfo,
    sessionInfo: session.sessionInfo,
  });

  return { assistantMessage, response };
}
```

---

## Direct API (Any Language)

For languages without an SDK, use the REST API directly.

### Record a Completion

```bash
POST https://app.freeplay.ai/api/v2/projects/{project_id}/sessions/{session_id}/completions

{
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ],
  "inputs": {"user_message": "Hello"},
  "response_info": {
    "model": "gpt-4",
    "provider": "openai",
    "latency_ms": 543
  }
}
```

### Record a Trace

```bash
POST https://app.freeplay.ai/api/v2/projects/{project_id}/sessions/{session_id}/traces

{
  "input": "User's question",
  "agent_name": "research_agent",
  "kind": "default",
  "custom_metadata": {"key": "value"}
}
```

### Record a Tool Trace

```bash
POST https://app.freeplay.ai/api/v2/projects/{project_id}/sessions/{session_id}/traces

{
  "input": "{\"query\": \"search term\"}",
  "agent_name": "web_search",
  "kind": "tool",
  "parent_trace_id": "parent-trace-uuid"
}
```

See the full API reference at: https://docs.freeplay.ai/reference

---

## Key SDK Methods Reference

| Operation | Python SDK | JavaScript SDK |
|-----------|-----------|---------------|
| Initialize client | `Freeplay(freeplay_api_key=..., api_base=...)` | `new Freeplay({freeplayApiKey, apiBase})` |
| Create session | `fp_client.sessions.create()` | `fpClient.sessions.create()` |
| Create trace | `session.create_trace(input, agent_name)` | `session.createTrace({input, agentName})` |
| Create tool trace | `session.create_trace(input, agent_name, kind="tool", parent_id=...)` | `session.createTrace({input, agentName, kind: "tool", parentId: ...})` |
| Fetch prompt | `fp_client.prompts.get_formatted(project_id, template_name, environment, variables, history)` | `fpClient.prompts.getFormatted({projectId, templateName, environment, variables, history})` |
| Record completion | `fp_client.recordings.create(RecordPayload(...))` | `fpClient.recordings.create({...})` |
| Record trace output | `trace.record_output(project_id, output)` | `trace.recordOutput({projectId, output})` |
| Add feedback (completion) | `fp_client.customer_feedback.update(completion_id, feedback)` | `fpClient.customerFeedback.update({completionId, feedback})` |
| Add feedback (trace) | `fp_client.customer_feedback.update_trace(project_id, trace_id, feedback)` | `fpClient.customerFeedback.updateTrace({projectId, traceId, feedback})` |

## Further Reading

- Freeplay SDK docs: https://docs.freeplay.ai/reference/sdk-setup
- Code recipes: https://docs.freeplay.ai/docs/single-prompt
- Sessions, Traces, Completions: https://docs.freeplay.ai/docs/sessions-traces-and-completions
- Python SDK: https://github.com/freeplay-ai/freeplay-python-sdk
- Node SDK: https://github.com/freeplay-ai/freeplay-node-sdk
