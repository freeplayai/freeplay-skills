# Google ADK + Freeplay Integration Reference

Reference patterns for integrating Freeplay with Google's Agent Development Kit (ADK). The `freeplay-python-adk` package provides automatic OpenTelemetry instrumentation and an optional Freeplay-managed agent class.

## Contents
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Core Pattern: Observability (Automatic)](#core-pattern-observability-automatic)
- [Core Pattern: Prompt Management (Optional)](#core-pattern-prompt-management-optional)
- [Multi-Agent with Prompt Management](#multi-agent-with-prompt-management)
- [Key Concepts](#key-concepts)
- [What Gets Logged](#what-gets-logged)
- [Notes](#notes)
- [Resources](#resources)

---

## Prerequisites

```bash
pip install freeplay-python-adk google-adk
```

## Environment Variables

```bash
export FREEPLAY_API_URL="https://app.freeplay.ai/api"  # ⚠️ /api suffix required
export FREEPLAY_API_KEY="fp-your-key-here"
export FREEPLAY_PROJECT_ID="your-project-id"

# Google Cloud / Gemini (existing ADK setup):
export GOOGLE_CLOUD_PROJECT="your-gcp-project"
# Or for AI Studio: export GOOGLE_API_KEY="your-api-key"
```

---

## Core Pattern: Observability (Automatic)

Add Freeplay observability to any existing ADK agent with no changes to agent code:

```python
from freeplay_python_adk.client import FreeplayADK
from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
from google.adk.agents import Agent
from google.adk.runners import App
from google.adk.tools import google_search

# Initialize Freeplay observability (call before any agent execution)
FreeplayADK.initialize_observability()

# Define agent as usual — no Freeplay-specific changes needed
root_agent = Agent(
    name="research_assistant",
    model="gemini-2.5-flash",
    instruction="You are a helpful research assistant. Use search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search],
)

# Add FreeplayObservabilityPlugin to App
app = App(
    name="research_app",
    root_agent=root_agent,
    plugins=[FreeplayObservabilityPlugin()],
)
```

All agent activity (LLM calls, tool calls, traces) now flows to Freeplay automatically.

---

## Core Pattern: Prompt Management (Optional)

Replace `Agent` / `LlmAgent` with `FreeplayLLMAgent` to manage prompts from the Freeplay UI instead of hardcoding in code:

```python
from freeplay_python_adk.client import FreeplayADK
from freeplay_python_adk.freeplay_llm_agent import FreeplayLLMAgent

FreeplayADK.initialize_observability()

root_agent = FreeplayLLMAgent(
    name="social_product_researcher",
    tools=[tavily_search],
)
```

**Freeplay prompt template setup** (in the Freeplay UI):

The template needs three elements:

1. **System message** — Agent instructions (what would be the `instruction` parameter):
   ```
   You are a social media product researcher...
   {{agent_context}}
   ```

2. **`{{agent_context}}` variable** — Add at the bottom of the system message. Passes ongoing agent context through at runtime.

3. **History block** — Add a new message with role set to `history`. Ensures past conversation messages are included.

---

## Multi-Agent with Prompt Management

Each agent can have its own Freeplay-managed prompt:

```python
from freeplay_python_adk.client import FreeplayADK
from freeplay_python_adk.freeplay_llm_agent import FreeplayLLMAgent
from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
from google.adk.runners import App

FreeplayADK.initialize_observability()

planner_agent = FreeplayLLMAgent(name="research_planner", tools=[])
researcher_agent = FreeplayLLMAgent(name="web_researcher", tools=[tavily_search])
writer_agent = FreeplayLLMAgent(name="report_writer", tools=[])

app = App(
    name="research_pipeline",
    root_agent=planner_agent,
    plugins=[FreeplayObservabilityPlugin()],
)
```

---

## Key Concepts

**Observability initialization:**
- `FreeplayADK.initialize_observability()` — Sets up OpenTelemetry tracing. Call once, before any agent execution.
- `FreeplayObservabilityPlugin()` — ADK plugin passed to `App(plugins=[...])`. Captures agent execution events via ADK's `BasePlugin` interface.

**Prompt management agent:**
- `FreeplayLLMAgent` — Extends ADK's `LlmAgent`. Retrieves prompt from Freeplay by matching the agent's `name` to a Freeplay template name.
- `{{agent_context}}` — Special variable in the Freeplay template that receives the ongoing agent execution context at runtime.
- History block — A message with role `history` in the Freeplay template ensures conversation history is passed through.

**Model and model parameters are managed in Freeplay** for all integrations. `FreeplayLLMAgent` does not need `model=` — the model, provider, and parameters (temperature, max_tokens, etc.) are all configured in the Freeplay UI and fetched at runtime.

**Two integration levels:**
- **Observability only:** `FreeplayADK.initialize_observability()` + `FreeplayObservabilityPlugin()`. Zero changes to existing agent definitions.
- **Observability + prompt management:** Also replace `Agent`/`LlmAgent` with `FreeplayLLMAgent`. Prompts, model, and model parameters all managed in Freeplay.

---

## What Gets Logged

- Agent traces with full execution flow
- LLM completions (prompt, response, tokens, latency)
- Tool call inputs and outputs
- Multi-agent parent-child relationships
- Prompt template linkage (when using `FreeplayLLMAgent`)

## Notes

Adapt these patterns to the user's existing code. Key things that vary:
- Agent definitions (tools, names, descriptions)
- Template names (must match between code and Freeplay project)
- Google Cloud vs AI Studio authentication
- Single-agent vs multi-agent architecture
- Whether to use prompt management or observability-only

The observability-only pattern requires no changes to existing agent code — just add the two initialization lines and the plugin.

## Resources

- [Freeplay ADK Integration Docs](https://docs.freeplay.ai/developer-resources/integrations/adk)
- [Google ADK Freeplay Guide](https://google.github.io/adk-docs/integrations/freeplay/)
- [Sample ADK Agent Repo (with Freeplay)](https://github.com/freeplayai/freeplay-google-demo)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
