# LangGraph + Freeplay Integration Reference

Reference patterns for integrating Freeplay with LangGraph. The `freeplay-langgraph` package provides automatic instrumentation — define agents with Freeplay-managed prompts and all traces are captured automatically.

## Contents
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Core Pattern: Agent with Tools](#core-pattern-agent-with-tools)
- [Core Pattern: Simple Prompt (Non-Agent)](#core-pattern-simple-prompt-non-agent)
- [Multi-Turn Conversation](#multi-turn-conversation)
- [Streaming](#streaming)
- [Key Concepts](#key-concepts)
- [What Gets Logged](#what-gets-logged)
- [Notes](#notes)
- [Resources](#resources)

---

## Prerequisites

```bash
pip install freeplay-langgraph langchain-openai langchain-core
```

## Environment Variables

```bash
export FREEPLAY_API_URL="https://app.freeplay.ai/api"  # ⚠️ /api suffix required
export FREEPLAY_API_KEY="fp-your-key-here"
export FREEPLAY_PROJECT_ID="your-project-id"
export OPENAI_API_KEY="sk-your-openai-key"
```

---

## Core Pattern: Agent with Tools

```python
from freeplay_langgraph import FreeplayLangGraph
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# Define tools
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    weather_data = {
        "San Francisco": "Sunny, 68°F",
        "New York": "Cloudy, 55°F",
    }
    return weather_data.get(city, f"Weather data not available for {city}")

@tool
def search_knowledge_base(query: str) -> str:
    """Search internal knowledge base for information."""
    return "We're open Monday-Friday 9am-5pm EST"

# Initialize client
freeplay = FreeplayLangGraph()

# Create agent with Freeplay-managed prompt
agent = freeplay.create_agent(
    prompt_name="weather-assistant",     # Template name in Freeplay
    variables={                          # Default template variables
        "default_location": "San Francisco",
        "temperature_unit": "Fahrenheit",
    },
    tools=[get_weather, search_knowledge_base],
    environment="production",            # Or "staging", "latest"
)

# Invoke — traces sent automatically to Freeplay
result = agent.invoke({
    "messages": [HumanMessage(content="What's the weather in Tokyo?")]
})
response = result["messages"][-1].content
```

Async variant: use `await agent.ainvoke(...)` with the same arguments.

---

## Core Pattern: Simple Prompt (Non-Agent)

For single LLM calls without agent tools:

```python
freeplay = FreeplayLangGraph()

response = freeplay.invoke(
    prompt_name="sentiment-analyzer",
    variables={"text": "This product is amazing!"},
    environment="production",
)
print(response.content)
```

Async variant: `await freeplay.ainvoke(...)`.

---

## Multi-Turn Conversation

Maintain message history across turns — each turn is logged under the same session:

```python
agent = freeplay.create_agent(
    prompt_name="weather-assistant",
    tools=[get_weather, search_knowledge_base],
    environment="production",
)

messages = []

# Turn 1
messages.append(HumanMessage(content="What's the weather in San Francisco?"))
result = agent.invoke({"messages": messages})
messages = result["messages"]

# Turn 2 — agent has context from turn 1
messages.append(HumanMessage(content="What about New York?"))
result = agent.invoke({"messages": messages})
messages = result["messages"]
```

---

## Streaming

Stream agent responses token-by-token:

```python
for chunk in agent.stream({
    "messages": [HumanMessage(content="Tell me about the weather in London")]
}):
    if "messages" in chunk and chunk["messages"]:
        last_message = chunk["messages"][-1]
        if hasattr(last_message, "content") and last_message.content:
            print(last_message.content, end="", flush=True)
```

---

## Key Concepts

**FreeplayLangGraph client:**
- `FreeplayLangGraph()` — Initializes with env vars (`FREEPLAY_API_URL`, `FREEPLAY_API_KEY`, `FREEPLAY_PROJECT_ID`)
- Can also pass credentials explicitly: `FreeplayLangGraph(freeplay_api_url=..., freeplay_api_key=..., project_id=...)`

**Agent creation:**
- `freeplay.create_agent(prompt_name, tools, variables, environment)` — Creates a LangGraph agent with a Freeplay-managed prompt
- `prompt_name` must match a template name in your Freeplay project
- `variables` are default values for the prompt template; override per-invocation as needed
- Agent name in Freeplay comes from the prompt template name

**Simple invocation:**
- `freeplay.invoke(prompt_name, variables, environment)` — Single LLM call without agent tools
- Returns the LLM response message directly

**Model and model parameters are managed in Freeplay** for all integrations. Neither `create_agent` nor `invoke` need a model argument — the model, provider, and parameters (temperature, max_tokens, etc.) are configured in the Freeplay UI and fetched at runtime from the prompt template.

**Automatic instrumentation:**
- All agent invocations, LLM calls, and tool calls are traced automatically via OpenTelemetry
- No manual recording calls needed

---

## What Gets Logged

- Sessions grouped by conversation
- Traces for each agent invocation
- Completions for every LLM call within the agent
- Tool call inputs and outputs
- Latency and token usage
- Prompt template linkage (which Freeplay template was used)

## Notes

Adapt these patterns to the user's existing code. Key things that vary:
- Tool definitions (replace examples with user's actual tools)
- Template names and variables (must match what's in their Freeplay project)
- Environment names ("production", "staging", "latest")
- Sync vs async (use `ainvoke`/`astream` for async codebases)
- Error handling (wrap invocations in try/except as appropriate)

## Resources

- [Freeplay LangGraph Docs](https://docs.freeplay.ai/developer-resources/integrations/langgraph)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Freeplay Prompt Management](https://docs.freeplay.ai/core-concepts/prompt-management/managing-prompts)
