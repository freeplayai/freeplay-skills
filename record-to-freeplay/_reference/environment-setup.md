# Environment Variable Setup

Provide these instructions using values from `.freeplay/environment-config.json`.

## Required Variables (All Frameworks)

```
FREEPLAY_API_KEY={FREEPLAY_API_KEY}
FREEPLAY_PROJECT_ID={FREEPLAY_PROJECT_ID}
```

## Framework-Specific Variables

**LangGraph** (`freeplay-langgraph`):
```
FREEPLAY_API_URL={FREEPLAY_API_BASE}
```

**Google ADK** (`freeplay-python-adk`):
```
FREEPLAY_API_BASE={FREEPLAY_API_BASE}
```

**Vercel AI SDK** (`@freeplayai/vercel`):
```
# For custom domains:
FREEPLAY_OTEL_ENDPOINT={FREEPLAY_API_BASE}/v0/otel/v1/traces
```

**Vanilla Python SDK** (`freeplay`):
```
FREEPLAY_API_BASE={FREEPLAY_API_BASE}
```

## Important

API URLs must include the `/api` suffix:
- Correct: `https://app.freeplay.ai/api`
- Wrong: `https://app.freeplay.ai`

## Where to Get Credentials

- Account API keys: `{FREEPLAY_BASE_URL}/settings/api-access`
- Project service accounts: `{FREEPLAY_BASE_URL}/projects/{FREEPLAY_PROJECT_ID}/service_accounts`

These should already be set if onboarding Step 1.5 was completed. If not, add to `~/.bashrc`, `~/.zshrc`, or `.env` file.
