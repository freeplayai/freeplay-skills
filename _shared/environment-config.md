# Environment Configuration

Shared workflow for loading or creating `.freeplay/environment-config.json`. Used by all skills that need Freeplay credentials and URLs.

## Loading Existing Config

Read `.freeplay/environment-config.json` for:
- `FREEPLAY_BASE_URL` — Base URL for UI links (e.g., `https://app.freeplay.ai`)
- `FREEPLAY_API_BASE` — API URL for SDK calls (e.g., `https://app.freeplay.ai/api`)
- `FREEPLAY_PROJECT_ID` — Project identifier
- `FREEPLAY_API_KEY` — API key
- `domain` — Domain for constructing URLs (e.g., `app`, `dev`, `custom`)
- `default_environment` — Deployment target (default: `latest`)

## If Config Missing

Present this dialog:

```
No environment configuration found (.freeplay/environment-config.json)

Would you like to use defaults or configure now?

1. Use defaults (app.freeplay.ai)
2. Configure environment now (recommended)
3. Run /freeplay-onboarding for full setup

Choice [1-3]:
```

**If defaults:** domain = `app`, FREEPLAY_BASE_URL = `https://app.freeplay.ai`, FREEPLAY_API_BASE = `https://app.freeplay.ai/api`, default_environment = `latest`

**If configure:** Run the configuration flow below.

## Configuration Flow

**Step 1 — Domain:**

```
Which Freeplay deployment are you using?

1. Production (app.freeplay.ai) - Most common
2. Custom domain - Enterprise deployments (e.g., acme.freeplay.ai)

Choice [1-2]:
```

- Production → domain = `app`
- Custom → prompt for subdomain

**Step 2 — Project ID:**

Replace `{domain}` with actual domain when displaying:

```
Enter your Freeplay Project ID:
You can find this on your project home page at https://{domain}.freeplay.ai/projects
```

**Step 3 — API key:**

Replace `{domain}` and `{project_id}` with actual values:

```
Enter your Freeplay API Key (format: fp-...):

Get your key from:
  - Account API keys: https://{domain}.freeplay.ai/settings/api-access
  - Project service accounts: https://{domain}.freeplay.ai/projects/{project_id}/service_accounts
```

**Step 4 — Construct URLs:**

```
base_url = https://{domain}.freeplay.ai
api_base = https://{domain}.freeplay.ai/api
```

**Step 5 — Save config and display env vars:**

Create `.freeplay/environment-config.json`:

```json
{
  "domain": "{domain}",
  "project_id": "{project_id}",
  "api_key": "fp-...",
  "FREEPLAY_BASE_URL": "https://{domain}.freeplay.ai",
  "FREEPLAY_API_BASE": "https://{domain}.freeplay.ai/api",
  "FREEPLAY_PROJECT_ID": "{project_id}",
  "FREEPLAY_API_KEY": "fp-...",
  "default_environment": "latest",
  "configured_at": "ISO timestamp"
}
```

Display to user:

```
Environment configured!
  Domain: {domain}.freeplay.ai
  Project ID: {project_id}

Add these environment variables to your shell (~/.bashrc, ~/.zshrc, or .env):

export FREEPLAY_BASE_URL="https://{domain}.freeplay.ai"
export FREEPLAY_API_BASE="https://{domain}.freeplay.ai/api"
export FREEPLAY_PROJECT_ID="{project_id}"
export FREEPLAY_API_KEY="{api_key}"

Note: FREEPLAY_API_BASE includes /api suffix (for SDK calls).
      FREEPLAY_BASE_URL is without /api (for UI links).
```

## Quick Links Pattern

Use these URL patterns throughout all skills:

```
Project Home: {FREEPLAY_BASE_URL}/projects/{project_id}/home
Sessions:     {FREEPLAY_BASE_URL}/projects/{project_id}/sessions
Templates:    {FREEPLAY_BASE_URL}/projects/{project_id}/templates
API Keys:     {FREEPLAY_BASE_URL}/settings/api-access
Service Accts: {FREEPLAY_BASE_URL}/projects/{project_id}/service_accounts
```
