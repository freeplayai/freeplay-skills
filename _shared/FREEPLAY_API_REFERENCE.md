# Freeplay API Reference

Top-level reference for the Freeplay REST API. Other skills should read this file when they need to construct or understand Freeplay API calls.

**Base URL**: `https://app.freeplay.ai`
**Auth**: `Authorization: Bearer <FREEPLAY_API_KEY>` on every request
**Content-Type**: `application/json`

---

## Endpoint Map

| Task | Method | Endpoint |
|------|--------|----------|
| List projects | GET | `/api/v2/projects/all` |
| Create project | POST | `/api/v2/projects` |
| Get project | GET | `/api/v2/projects/{project_id}` |
| List models | GET | `/api/v2/models` |
| Record completion | POST | `/api/v2/projects/{project_id}/sessions/{session_id}/completions` |
| Update completion | POST | `/api/v2/projects/{project_id}/completions/{completion_id}` |
| Record trace | POST | `/api/v2/projects/{project_id}/sessions/{session_id}/traces/id/{trace_id}` |
| Update trace | PATCH | `/api/v2/projects/{project_id}/sessions/{session_id}/traces/id/{trace_id}` |
| Update session metadata | PATCH | `/api/v2/projects/{project_id}/sessions/id/{session_id}/metadata` |
| Update trace metadata | PATCH | `/api/v2/projects/{project_id}/sessions/{session_id}/traces/id/{trace_id}/metadata` |
| Completion feedback | POST | `/api/v2/projects/{project_id}/completion-feedback/id/{completion_id}` |
| Trace feedback | POST | `/api/v2/projects/{project_id}/trace-feedback/id/{trace_id}` |
| List prompt templates | GET | `/api/v2/projects/{project_id}/prompt-templates` |
| Create prompt template | POST | `/api/v2/projects/{project_id}/prompt-templates` |
| Get prompt template | GET | `/api/v2/projects/{project_id}/prompt-templates/id/{template_id}` |
| List template versions | GET | `/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions` |
| Create template version | POST | `/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions` |
| Get template version | GET | `/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions/{version_id}` |
| Get bound version | POST | `/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions/{version_id}` |

---

## Key Concepts

**Sessions** — Containers for related LLM interactions. Not created explicitly; generate a UUID v4 client-side and use it as `session_id`. The session is created implicitly on first use.

**Completions** — Individual LLM calls (prompt + response). Live inside sessions. Optionally generate `completion_id` client-side.

**Traces** — Higher-level operations (agent steps, tool calls) that may contain multiple completions. Client-generated UUIDs. Use `parent_id` to build hierarchies.

**Prompt Templates** — Named containers that hold **versions**. Each version has actual messages, model config, and parameters. Versions deploy to **environments** (e.g. "staging", "production"). Identical versions are automatically deduplicated.

---

## Conventions

**Client-side UUIDs**: Session IDs, trace IDs, completion IDs, project IDs, and template IDs can all be generated client-side as UUID v4. This avoids round-trips and enables fire-and-forget logging.

**Message formats**: The `messages` field in Record Completion accepts OpenAI (role/content), Anthropic (role/content with content blocks), Simple, Vertex, and Bedrock formats. The API normalizes internally.

**Version deduplication**: Creating a prompt template version that's identical to an existing one returns the existing version instead of a duplicate.

**Metadata merging**: PATCH metadata endpoints merge keys — existing keys overwritten, new keys added, unmentioned keys preserved.

**Pagination**: List endpoints accept `page` (default 1) and `page_size` (default 30) query params. Responses include `pagination: {page, page_size, has_next}`.

**Feedback**: Use key `freeplay_feedback` with value `"positive"` or `"negative"` for thumbs up/down. Additional keys stored as custom feedback.

---

## Decision Guide

- **Log LLM calls** → Record Completion. Generate a session_id, include messages + call_info.
- **Log agent workflows** → Record Trace for the agent step, Record Completion for LLM calls within it. Link via `trace_info.trace_id` and `parent_id`.
- **Manage prompts** → Create a Prompt Template (container), then create Versions with content. Deploy versions to environments.
- **Get a prompt with variables filled in** → Get Bound Version (POST to version endpoint with variables in body).
- **Add user feedback** → Completion Feedback or Trace Feedback. Include `freeplay_feedback`.
- **Tag sessions/traces with extra info** → Update Session Metadata or Update Trace Metadata (PATCH).
- **Append to an existing completion** → Update Completion (add new messages or eval results).

---

## Endpoint Details

### Configuration

#### List Projects
```
GET /api/v2/projects/all
```
Response:
```json
{"projects": [{"id": "uuid", "name": "My Project"}, ...]}
```

#### Create Project
```
POST /api/v2/projects
```
```json
{
  "name": "My Project",
  "is_private": false,
  "id": "optional-client-uuid"
}
```
Response (201): Full project detail including `id`, `name`, `is_private`, `freeplay_spend_limit_usd`, `data_retention_days`, `enable_eval_insights`, `enable_review_insights`.

#### Get Project
```
GET /api/v2/projects/{project_id}
```
Response: Same shape as Create Project response.

#### List Models
```
GET /api/v2/models?page=1&page_size=30
```
Response:
```json
{
  "data": [{
    "id": "uuid", "name": "gpt-4o", "display_name": "GPT-4o",
    "provider_name": "openai", "supports_tool_use": true,
    "model_family": "gpt-4o", "model_version": "2024-08-06",
    "created_at": "2024-01-01T00:00:00Z"
  }, ...],
  "pagination": {"page": 1, "page_size": 30, "has_next": false}
}
```

---

### Observability

#### Record Completion
```
POST /api/v2/projects/{project_id}/sessions/{session_id}/completions
```
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ],
  "inputs": {"user_query": "Hello"},
  "prompt_info": {
    "prompt_template_version_id": "uuid",
    "environment": "production"
  },
  "call_info": {
    "model": "gpt-4o",
    "provider": "openai",
    "start_time": 1700000000.0,
    "end_time": 1700000001.5,
    "usage": {"prompt_tokens": 25, "completion_tokens": 12},
    "llm_parameters": {"temperature": 0.7}
  },
  "session_info": {"custom_metadata": {"user_id": "u123"}},
  "trace_info": {"trace_id": "uuid"},
  "eval_results": {"quality": "good"},
  "completion_id": "optional-client-uuid",
  "parent_id": "optional-parent-completion-uuid",
  "tool_schema": null,
  "output_schema": null,
  "media_inputs": null
}
```
All fields except `messages` are optional. Response (201):
```json
{"completion_id": "uuid"}
```

#### Update Completion
```
POST /api/v2/projects/{project_id}/completions/{completion_id}
```
```json
{
  "new_messages": [{"role": "assistant", "content": "...streamed continuation"}],
  "eval_results": {"accuracy": 0.95}
}
```
Use for streaming (append messages) or post-hoc evals. Response: `{"completion_id": "uuid"}`.

#### Record Trace
```
POST /api/v2/projects/{project_id}/sessions/{session_id}/traces/id/{trace_id}
```
```json
{
  "input": {"query": "Find flights to Paris"},
  "output": {"result": "Found 3 flights..."},
  "parent_id": "optional-parent-trace-uuid",
  "agent_name": "travel-agent",
  "custom_metadata": {"region": "eu"},
  "eval_results": {"success": true},
  "name": "flight-search",
  "kind": "tool",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T10:00:05Z"
}
```
`input` and `output` are required (any JSON). `kind` set to `"tool"` for tool call traces. Response (201): empty.

#### Update Trace by ID
```
PATCH /api/v2/projects/{project_id}/sessions/{session_id}/traces/id/{trace_id}
```
```json
{
  "metadata": {"latency_ms": 1250},
  "feedback": {"freeplay_feedback": "positive"}
}
```

#### Update Session Metadata
```
PATCH /api/v2/projects/{project_id}/sessions/id/{session_id}/metadata
```
```json
{"user_tier": "premium", "ab_test": "variant_b"}
```
Body is a flat object of string/number/integer/boolean values. Merges with existing metadata.

#### Update Trace Metadata
```
PATCH /api/v2/projects/{project_id}/sessions/{session_id}/traces/id/{trace_id}/metadata
```
Same body format as session metadata.

#### Add Completion Feedback
```
POST /api/v2/projects/{project_id}/completion-feedback/id/{completion_id}
```
```json
{"freeplay_feedback": "positive", "comment": "Great answer"}
```
Response (201): `{"message": "..."}`.

#### Add Trace Feedback
```
POST /api/v2/projects/{project_id}/trace-feedback/id/{trace_id}
```
Same body format as completion feedback.

---

### Prompt Templates

#### List Prompt Templates
```
GET /api/v2/projects/{project_id}/prompt-templates?page=1&page_size=30
```
Response:
```json
{
  "data": [{"id": "uuid", "name": "my-template", "latest_template_version_id": "uuid"}, ...],
  "pagination": {"page": 1, "page_size": 30, "has_next": false}
}
```

#### Create Prompt Template
```
POST /api/v2/projects/{project_id}/prompt-templates
```
```json
{"name": "customer-support", "id": "optional-client-uuid"}
```
Creates the container only. Response (201): `{"id": "uuid"}`.

#### Get Prompt Template
```
GET /api/v2/projects/{project_id}/prompt-templates/id/{template_id}
```
Response: `{"id": "uuid", "name": "...", "latest_template_version_id": "uuid"}`.

#### List Template Versions
```
GET /api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions?page=1&page_size=30
```
Response: paginated array of `PlainPromptTemplate` objects (see Create Version response).

#### Create Template Version
```
POST /api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions
```
```json
{
  "template_messages": [
    {"role": "system", "content": "You are a support agent for {{company_name}}."},
    {"role": "user", "content": "{{user_message}}"}
  ],
  "model": "gpt-4o",
  "provider": "openai",
  "version_name": "v1.2",
  "version_description": "Added company context",
  "llm_parameters": {"temperature": 0.7, "max_tokens": 500},
  "tool_schema": null,
  "output_schema": null,
  "environments": ["staging", "production"]
}
```
`template_messages` is an array of `{role, content}` objects or `{"kind": "history"}` placeholders.
`environments` optionally deploys the version on creation.
Response (201): Full `PlainPromptTemplate`:
```json
{
  "prompt_template_id": "uuid",
  "prompt_template_version_id": "uuid",
  "prompt_template_name": "customer-support",
  "version_name": "v1.2",
  "version_description": "Added company context",
  "metadata": {
    "provider": "openai", "model": "gpt-4o",
    "params": {"temperature": 0.7, "max_tokens": 500}
  },
  "format_version": 2,
  "project_id": "uuid",
  "content": [
    {"role": "system", "content": "You are a support agent for {{company_name}}."},
    {"role": "user", "content": "{{user_message}}"}
  ]
}
```

#### Get Template Version
```
GET /api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions/{version_id}
```
Response: Same `PlainPromptTemplate` shape as above.

#### Get Bound Template Version
```
POST /api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions/{version_id}?format=openai
```
```json
{"company_name": "Acme Corp", "user_message": "How do I reset my password?"}
```
Returns messages with `{{variables}}` substituted, formatted for the requested provider. Query params: `environment` (optional), `format` (optional, e.g. "openai").

---

## Worked Examples

### Example 1: Log a simple LLM call

```bash
SESSION_ID=$(uuidgen)

curl -X POST "https://app.freeplay.ai/api/v2/projects/${PROJECT_ID}/sessions/${SESSION_ID}/completions" \
  -H "Authorization: Bearer ${FREEPLAY_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"},
      {"role": "assistant", "content": "The capital of France is Paris."}
    ],
    "call_info": {
      "model": "gpt-4o",
      "provider": "openai",
      "start_time": 1700000000.0,
      "end_time": 1700000001.5,
      "usage": {"prompt_tokens": 25, "completion_tokens": 12}
    }
  }'
```

### Example 2: Agent trace with nested completion and tool call

```bash
SESSION_ID=$(uuidgen)
TRACE_ID=$(uuidgen)
TOOL_TRACE_ID=$(uuidgen)

# 1. Record the top-level agent trace
curl -X POST ".../sessions/${SESSION_ID}/traces/id/${TRACE_ID}" \
  -d '{
    "input": {"query": "Find flights to Paris"},
    "output": {"result": "Found 3 flights"},
    "agent_name": "travel-agent",
    "start_time": "2024-01-15T10:00:00Z",
    "end_time": "2024-01-15T10:00:05Z"
  }'

# 2. Record a completion linked to the trace
curl -X POST ".../sessions/${SESSION_ID}/completions" \
  -d '{
    "messages": [
      {"role": "user", "content": "Find flights to Paris"},
      {"role": "assistant", "content": null, "tool_calls": [{"function": {"name": "search_flights"}}]}
    ],
    "trace_info": {"trace_id": "'"${TRACE_ID}"'"},
    "call_info": {"model": "gpt-4o", "provider": "openai"}
  }'

# 3. Record the tool call as a child trace
curl -X POST ".../sessions/${SESSION_ID}/traces/id/${TOOL_TRACE_ID}" \
  -d '{
    "input": {"function": "search_flights", "args": {"destination": "Paris"}},
    "output": {"flights": [{"airline": "AF", "price": 450}]},
    "parent_id": "'"${TRACE_ID}"'",
    "kind": "tool",
    "name": "search_flights"
  }'
```

### Example 3: Create and use a prompt template

```bash
# 1. Create template
TEMPLATE_ID=$(curl -s -X POST ".../projects/${PROJECT_ID}/prompt-templates" \
  -d '{"name": "summarizer"}' | jq -r '.id')

# 2. Create version deployed to staging
VERSION_ID=$(curl -s -X POST ".../prompt-templates/id/${TEMPLATE_ID}/versions" \
  -d '{
    "template_messages": [
      {"role": "system", "content": "Summarize the following text in {{style}} style."},
      {"role": "user", "content": "{{text}}"}
    ],
    "model": "claude-sonnet-4-5-20250514",
    "provider": "anthropic",
    "environments": ["staging"]
  }' | jq -r '.prompt_template_version_id')

# 3. Get bound version with variables filled in
curl -X POST ".../prompt-templates/id/${TEMPLATE_ID}/versions/${VERSION_ID}?format=anthropic" \
  -d '{"style": "bullet point", "text": "The quick brown fox..."}'
```
