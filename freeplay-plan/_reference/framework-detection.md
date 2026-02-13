# Framework Detection Patterns

This guide provides samples of detecting common AI frameworks within a code base. This is not extensive and should be used as a starting point.
There is the possibility that no frameworks are being used and none of these apply.

## LangGraph

**Primary Detection:**
```bash
Grep pattern="from langgraph\\.(graph|prebuilt)" glob="**/*.py" output_mode="files_with_matches"
```

**Confirm Usage:**
```bash
Grep pattern="StateGraph|MessageGraph|ToolNode" glob="**/*.py" output_mode="count"
```

**Confidence:**
- Count >= 2: High confidence
- Count == 1: Medium confidence
- Import only: Low confidence (may be unused)

**Version Detection:**
```bash
Grep pattern="langgraph[>=<]" glob="**/requirements*.txt" output_mode="content"
Grep pattern="\"langgraph\":" glob="**/pyproject.toml" output_mode="content"
```

---

## LangChain (without LangGraph)

**Primary Detection:**
```bash
Grep pattern="from langchain\\.(chains|agents|llms|chat_models)" glob="**/*.py" output_mode="files_with_matches"
```

**Confirm Usage:**
```bash
Grep pattern="LLMChain|ConversationChain|ChatOpenAI|ChatAnthropic" glob="**/*.py" output_mode="count"
```

**Confidence:**
- Count >= 3: High confidence
- Count 1-2: Medium confidence

**Distinguish from LangGraph:**
- If LangGraph detected: Framework = LangGraph (superset)
- If only LangChain detected: Framework = LangChain

---

## Vercel AI SDK

**Primary Detection:**
```bash
Grep pattern="from ['\"]ai['\"]" glob="**/*.{ts,tsx,js,jsx}" output_mode="files_with_matches"
```

**Confirm Usage:**
```bash
Grep pattern="generateText|streamText|generateObject" glob="**/*.{ts,tsx,js,jsx}" output_mode="count"
```

**Confidence:**
- Count >= 1: High confidence (direct usage)
- Import only: Medium confidence

**Version Detection:**
```bash
Grep pattern="\"ai\":" glob="**/package.json" output_mode="content"
```

---

## Vanilla OpenAI SDK

**Primary Detection:**
```bash
Grep pattern="from openai import" glob="**/*.py" output_mode="files_with_matches"
Grep pattern="import openai" glob="**/*.py" output_mode="files_with_matches"
```

**Confirm Usage (Python):**
```bash
Grep pattern="openai\\.chat\\.completions\\.create|client\\.chat\\.completions\\.create" glob="**/*.py" output_mode="count"
```

**Confirm Usage (TypeScript/JavaScript):**
```bash
Grep pattern="new OpenAI\\(|openai\\.chat\\.completions\\.create" glob="**/*.{ts,tsx,js,jsx}" output_mode="count"
```

**Confidence:**
- Direct `.create` calls found: High confidence
- Only import: Low confidence (may use framework wrapper)

**Exclude Framework Wrappers:**
- If LangChain/LangGraph detected with OpenAI import: Framework = LangGraph/LangChain
- Only mark as "vanilla" if no framework detected

---

## Vanilla Anthropic SDK

**Primary Detection (Python):**
```bash
Grep pattern="from anthropic import|import anthropic" glob="**/*.py" output_mode="files_with_matches"
```

**Primary Detection (TypeScript):**
```bash
Grep pattern="from ['\"]@anthropic-ai/sdk['\"]|import.*Anthropic.*from" glob="**/*.{ts,tsx,js,jsx}" output_mode="files_with_matches"
```

**Confirm Usage:**
```bash
Grep pattern="messages\\.create|anthropic\\.messages\\.create" glob="**/*.{py,ts,tsx,js,jsx}" output_mode="count"
```

**Confidence:**
- Direct `.messages.create` calls: High confidence
- Only import: Low confidence

---

## Google ADK (Agent Development Kit)

**Primary Detection:**
```bash
Grep pattern="from google\\.adk|import google\\.adk" glob="**/*.py" output_mode="files_with_matches"
```

**Confirm Usage:**
```bash
Grep pattern="Agent\\(|create_agent\\(|adk\\." glob="**/*.py" output_mode="count"
```

**Confidence:**
- Count >= 1: High confidence
- Import only: Medium confidence

---

## CrewAI

**Primary Detection:**
```bash
Grep pattern="from crewai import|import crewai" glob="**/*.py" output_mode="files_with_matches"
```

**Confirm Usage:**
```bash
Grep pattern="Agent\\(|Task\\(|Crew\\(" glob="**/*.py" output_mode="count"
```

**Confidence:**
- Count >= 2: High confidence
- Count == 1: Medium confidence

---

## Decision Tree

Use this logic to determine the primary framework:

```
1. Check for LangGraph
   └─ If found → Framework = LangGraph (stop)

2. Check for Vercel AI SDK
   └─ If found → Framework = Vercel AI SDK (stop)

3. Check for CrewAI or Google ADK
   └─ If found → Framework = [CrewAI|Google ADK] (stop)

4. Check for LangChain (without LangGraph)
   └─ If found → Framework = LangChain (stop)

5. Check for vanilla SDKs
   ├─ OpenAI found → Framework = Vanilla OpenAI
   ├─ Anthropic found → Framework = Vanilla Anthropic
   └─ Both found → Framework = Multiple vanilla SDKs

6. None found
   └─ Unknown or no LLM usage detected
```

---

## Model Detection

Once framework is identified, detect which models are being used:

**GPT Models (OpenAI):**
```bash
Grep pattern="gpt-4|gpt-3\\.5-turbo|gpt-4o|o1-preview|o1-mini" glob="**/*.{py,ts,tsx,js,jsx}" output_mode="content" -A=2
```

**Claude Models (Anthropic):**
```bash
Grep pattern="claude-3-(opus|sonnet|haiku)|claude-2" glob="**/*.{py,ts,tsx,js,jsx}" output_mode="content" -A=2
```

**Extract model names from matches and deduplicate**

---

## Provider Detection

Based on imports and model names:

| Framework/SDK | Provider |
|---------------|----------|
| `langchain_openai` | OpenAI |
| `langchain_anthropic` | Anthropic |
| `from openai` | OpenAI |
| `from anthropic` | Anthropic |
| Model name `gpt-*` | OpenAI |
| Model name `claude-*` | Anthropic |

---

## Common Pitfalls

### False Positives

**Problem:** Finding imports that aren't actually used
**Solution:** Always confirm with usage patterns (count > 0)

**Example:**
```bash
# Don't trust this alone:
Grep pattern="from langgraph" output_mode="files_with_matches"

# Also check for actual usage:
Grep pattern="StateGraph\\(" output_mode="count"
```

### Multiple Frameworks

**Problem:** Codebase uses multiple frameworks
**Solution:** List all detected, mark primary as highest confidence

**Example:**
```json
{
  "framework_detected": {
    "primary": "langgraph",
    "confidence": "high",
    "secondary": ["vanilla_openai"],
    "notes": "LangGraph for main agent, vanilla OpenAI for simple completions"
  }
}
```

### Wrapper Functions

**Problem:** Code wraps SDK calls in helper functions
**Solution:** Search for both direct SDK calls and common wrapper patterns

**Example:**
```bash
# Search for wrappers
Grep pattern="def (call_llm|get_completion|chat|generate)" glob="**/*.py" output_mode="files_with_matches"

# Then inspect those files for actual SDK usage
```

---

## Example Detection Sequence

Here's a complete example of detecting LangGraph:

```bash
# Step 1: Check for LangGraph imports
Grep pattern="from langgraph" glob="**/*.py" output_mode="files_with_matches"
# Result: agents/main.py, agents/workflow.py

# Step 2: Confirm usage
Grep pattern="StateGraph\\(" glob="**/*.py" output_mode="count"
# Result: 3 matches

# Step 3: Detect version
Grep pattern="langgraph" glob="**/requirements*.txt" output_mode="content"
# Result: langgraph==0.2.16

# Step 4: Find model providers
Grep pattern="from langchain_(openai|anthropic)" glob="**/*.py" output_mode="files_with_matches"
# Result: agents/main.py (langchain_openai)

# Step 5: Detect models
Grep pattern="gpt-4|gpt-3.5" glob="**/*.py" output_mode="content"
# Result: gpt-4 in agents/main.py:45

# Conclusion:
# Framework: LangGraph v0.2.16
# Provider: OpenAI
# Models: gpt-4
# Confidence: High
```

---

## Tips for Accuracy

1. **Always combine import + usage checks** - Don't trust imports alone
2. **Use specific patterns** - `StateGraph\\(` is better than just `StateGraph`
3. **Check multiple file types** - Python AND TypeScript if it's a full-stack app
4. **Verify with version files** - Cross-reference with requirements.txt/package.json
5. **Distinguish frameworks** - LangGraph supersedes LangChain, don't mark both as primary
6. **Look for configuration** - Often model names are in config files, not code
