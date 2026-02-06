---
name: health-check
description: Assess the health, completeness, and production readiness of a Freeplay project across the data flywheel. Use when the user asks about project status, wants to know if their project is ready for production, asks what's missing in their Freeplay setup, wants a project health check, or asks "what should I set up next?" Also use when the user is first connecting a project to Freeplay.
---

# Freeplay Project Health Check

This skill performs a comprehensive assessment of a Freeplay project's health across all dimensions of the data flywheel: observability, datasets, evaluations, testing, and continuous improvement.

## When to use this skill

- "Is my project production ready?"
- "What's missing in my Freeplay setup?"
- "Check the health of project X"
- "How complete is my evaluation setup?"
- "Is my data flywheel working?"
- "What should I set up next?"
- When starting work on an unfamiliar project
- Before making significant changes to prompts or evaluations
- After onboarding a new project to Freeplay (AFTER initial integration)

## The Data Flywheel Mental Model

Freeplay enables continuous improvement through a connected data flywheel:

```
Production (Observability)
        ↓ Logs sessions/traces/completions
Monitoring & Review
        ↓ Identifies patterns, failures
Datasets (Curation)
        ↓ Failures and successes become test cases
Prompt and Agent Iteration (Improvement)
        ↓ New versions created
Test Runs (Validation)
        ↓ Results inform changes and prevent regressions
Deployment (Versioning)
        ↓ Controlled rollout
Production (Repeat)
```

A healthy project has all stages connected and flowing.

## Health Dimensions

Assess each dimension on a 3-level scale:
- **✅ Healthy**: Well-configured, active, no action needed
- **⚠️ Needs Attention**: Partially configured or showing warning signs
- **❌ Critical/Missing**: Not set up or blocking the flywheel

### 1. Prompt Management

**What to check:**
- At least one prompt template exists
- Templates have multiple versions (showing iteration)
- Versions are deployed to environments (dev, staging, prod, etc.)
- Clear naming and versioning conventions

**MCP tools to use:**
```
list_prompt_templates(project_id)
get_prompt_version(project_id, template_id, version_id)
```

**API calls:**
```bash
# List all environments to verify deployment targets exist
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/environments"

# Get version history for a specific template (to check iteration)
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions"
```

**What to look for:**
- `list_prompt_templates` returns templates with `latest_version_id` populated
- Each template's version shows deployed environments (check for prod/staging/dev)
- Multiple versions per template indicates active iteration
- Version names follow a pattern (e.g., semantic versioning, descriptive names)

**Scoring:**
- ✅ Multiple templates with versions deployed to multiple environments (or one template with lots of activity in the case of single prompt projects)
- ⚠️ Templates exist but only deployed to one environment, or no recent versions
- ❌ No templates, or templates with no deployed versions

### 2. Evaluation Setup

**What to check:**
- Evaluation criteria exist for key prompt templates/agents
- Multiple evaluation types configured or present in logs (model-graded, code, human)
- Evaluation criteria are enabled and running/published
- Sample rates are appropriate (not 0%)
- Insights generation is enabled at project and criteria level

**MCP tools to use:**
```
search_completions(project_id, limit=50) → check for evaluation results in logs
list_insights(project_id) → check if insights are being generated
```

**API calls:**
```bash
# List all evaluation criteria with their configuration
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/evaluation-criteria"

# Get project settings to check insight flags
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}"
```

**What to look for:**
- Evaluation criteria list shows `is_enabled: true` for active criteria
- Look for `type` field: "llm_eval", "code_eval", "user_eval", "auto_categorization"
- Check `sample_rate` is > 0 (1.0 = 100% of completions evaluated)
- Check `generate_insights` on criteria
- Project settings should have `enable_eval_insights` and `enable_review_insights` set to true
- Completions from `search_completions` should show evaluation scores

**Scoring:**
- ✅ 3+ evaluation criteria, insights enabled, consistent scoring
- ⚠️ 1-2 evaluation criteria, or insights disabled, or inconsistent results
- ❌ No evaluation criteria configured, or all evaluation criteria disabled

### 3. Observability (Production Logging)

**What to check:**
- Sessions, traces*, AND completions are each being logged (*except in the case of projects with a single prompt template)
- Recent activity (within last 7 days)
- Completions linked to prompt templates (not orphaned)
- Evaluation criteria running on production data
- Customer feedback and/or custom metadata being logged
- Cost and latency being tracked

**MCP tools to use:**
```
search_sessions(project_id, limit=20)
search_completions(project_id, limit=20)
search_traces(project_id, limit=20)
find_logging_issues(project_id, template_name=<main_template>) → identifies missing logged fields
```

**What to look for in search results:**
- `search_sessions`: Check count, most recent timestamp, presence of metadata
- `search_completions`: Check for:
  - `template_name` populated (not orphaned)
  - `environment` set (tracking deployment context)
  - Evaluation scores present in results
  - Cost and latency data populated
- `search_traces`: Check if traces exist (for multi-step/agentic projects)
- `find_logging_issues`: Returns specific missing fields with fix suggestions

**Date filtering for recency:**
Use the `start_date` parameter to check recent activity:
```
search_completions(project_id, limit=20, start_date="2026-01-28")
```

**Scoring:**
- ✅ Active logging (100+ sessions), recent activity, evaluations running, all key fields populated
- ⚠️ Some logging but sparse, or no recent activity, or completions not linked to prompt templates, or missing feedback/metadata
- ❌ No sessions/completions logged, or no activity in 30+ days

### 4. Dataset Coverage

**What to check:**
- At least one dataset exists
- Test cases exist in datasets that include inputs and output
- Various inputs in test cases cover key usage scenarios, based on what's happening in production logs

**API calls:**
```bash
# List all prompt-level datasets
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-datasets"

# List all agent-level datasets (for agentic projects)
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/agent-datasets"

# Get test cases for a specific prompt dataset (to count and inspect)
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-datasets/id/{dataset_id}/test-cases"

# Get test cases for a specific agent dataset
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/agent-datasets/id/{dataset_id}/test-cases"
```

**MCP tools to use:**
These are useful for comparing dataset coverage to production usage patterns:
```
search_completions(project_id, limit=50) → see what inputs are common in production
search_traces(project_id, limit=20) → for agent workflows
```

**What to look for:**
- Dataset list returns one or more datasets with meaningful names
- Test cases include both `inputs` and expected `output` (not just inputs)
- Compare test case inputs to production completion inputs for coverage gaps
- Look for dataset purposes: golden examples, failure cases, edge cases, red team

**Scoring:**
- ✅ 3+ datasets with 50+ total test cases, covering different purposes/scenarios
- ⚠️ 1-2 datasets, or fewer than 20 test cases each, or missing expected outputs
- ❌ No datasets, all datasets are empty, or fewer than 20 test cases total

### 5. Testing Cadence

**What to check:**
- Test runs being executed
- Recent test runs (within last 10 days)
- Multiple test runs per prompt template and/or agent (showing iteration)
- Test runs include evaluation results
- Comparison tests being created

**API calls:**
```bash
# List all test runs
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/test-runs"

# Get detailed results for a specific test run (includes evaluation scores)
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/test-runs/id/{test_run_id}"
```

**What to look for:**
- Test runs list shows multiple runs with recent `created_at` timestamps
- Same `prompt_name` appears in multiple runs (showing iteration)
- `summary_statistics` contains `auto_evaluation` and/or `human_evaluation` scores
- Look for paired runs with similar names (e.g., "baseline" vs "optimized") indicating A/B comparisons
- Check `sessions_count` matches expected dataset size

**Scoring:**
- ✅ 10+ test runs, recent activity (within 10 days), comparative testing evident
- ⚠️ 1-9 test runs, or no recent tests, or no comparisons
- ❌ No test runs ever executed

### 6. Continuous Improvement Signals

**What to check:**
- Insights being generated (eval insights, review insights)
- Prompt optimization runs attempted
- Human reviews being conducted (manual evaluation criteria scoring or notes present)
- Patterns being identified and addressed

**MCP tools to use:**
```
list_insights(project_id) → check for active insights
get_prompt_version(project_id, template_id, version_id) → check for optimized versions
search_completions(project_id, limit=50) → look for human evaluation scores
```

**API calls:**
```bash
# Get prompt template versions to check for optimization history
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions"

# Search completions with review_status filter (if available)
# Look for completions that have been manually reviewed
```

**What to look for:**
- `list_insights` returns insights with meaningful content (not empty)
- Prompt versions with names containing "Optimized" or created by optimization process
- Version descriptions mentioning optimization or improvement
- Completions showing `human_evaluation` or `manual_score` values
- Insights have `status: "active"` (not just orphaned/pruned)
- Multiple prompt versions over time (not just one static version)

**Scoring:**
- ✅ Active insights being created, prompt optimization used, human review scores present
- ⚠️ Some insights exist but not acted on, or no prompt optimization attempts, or sparse human reviews
- ❌ No insights, no optimization attempts, no human review activity

### 7. Configuration Completeness

**What to check:**
- API credentials working
- Environments being used (at least 1 prompt template deployed to prod at minimum)
- LLM provider credentials configured
- Project settings appropriate (data retention, spend limits, insights enabled)

**MCP tools to use:**
```
list_projects() → validates API credentials are working
list_prompt_templates(project_id) → check which environments have deployments
```

**API calls:**
```bash
# List all environments in the account
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/environments"

# Get project settings
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}"

# Get all templates deployed to production environment
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-templates/environment/production"
```

**What to look for:**
- MCP calls succeed (credentials valid)
- Environments list includes at least: production (or prod), and ideally staging/dev
- Project settings show:
  - `enable_eval_insights: true`
  - `enable_review_insights: true`
  - `data_retention_days` set appropriately
  - `freeplay_spend_limit_usd` configured if using Freeplay-hosted models
- At least one template deployed to production environment

**Scoring:**
- ✅ All credentials valid, 3+ environments with active deployments, insights enabled
- ⚠️ Missing some environments, or insight flags disabled, or no production deployment
- ❌ Invalid credentials, or no environments defined, or project misconfigured

## How to Perform the Health Check

### Step 1: Gather Project Context

First, identify the project. If not provided, ask the user or use `list_projects()` to show available projects.

### Step 2: Collect Data (Parallel)

Run these MCP calls in parallel to gather comprehensive data:

```
list_prompt_templates(project_id)
search_sessions(project_id, limit=50)
search_completions(project_id, limit=50)
search_traces(project_id, limit=20)
list_insights(project_id)
find_logging_issues(project_id) → optional, for deeper observability analysis
```

And these API calls (can be run in parallel):
```bash
# Project settings (insights flags, retention, limits)
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}"

# Environments
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/environments"

# Evaluation Criteria
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/evaluation-criteria"

# Prompt Datasets
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-datasets"

# Agent Datasets (for agentic projects)
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/agent-datasets"

# Test Runs
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/test-runs"
```

**Follow-up calls (based on initial results):**
```bash
# Get test case counts for each dataset
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-datasets/id/{dataset_id}/test-cases"

# Get version history for active templates
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/prompt-templates/id/{template_id}/versions"

# Get detailed test run results if needed
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/test-runs/id/{test_run_id}"
```

### Step 3: Analyze Each Dimension

For each dimension, evaluate against the scoring criteria and note specific findings.

### Step 4: Calculate Overall Health

Count the scores:
- **Production Ready**: 6-7 dimensions ✅, no ❌
- **Almost Ready**: 4-5 dimensions ✅, max 1 ❌
- **Needs Work**: 2-3 dimensions ✅, or 2+ ❌
- **Getting Started**: 0-1 dimensions ✅

### Step 5: Generate Recommendations

Based on gaps, provide prioritized recommendations:

1. **Critical (❌ items)**: Must fix before production
2. **Important (⚠️ items)**: Should address for reliability
3. **Optimization**: Nice-to-have improvements

## Output Format

Present results in this structure:

```
# Project Health Check: {Project Name}

## Overall Status: {Production Ready | Almost Ready | Needs Work | Getting Started}

## Flywheel Scorecard

| Dimension              | Status | Finding |
|------------------------|--------|---------|
| Prompt Management      | ✅/⚠️/❌ | Brief description |
| Evaluation Setup       | ✅/⚠️/❌ | Brief description |
| Observability          | ✅/⚠️/❌ | Brief description |
| Dataset Coverage       | ✅/⚠️/❌ | Brief description |
| Testing Cadence        | ✅/⚠️/❌ | Brief description |
| Continuous Improvement | ✅/⚠️/❌ | Brief description |
| Configuration          | ✅/⚠️/❌ | Brief description |

## Key Metrics

- **Prompt Templates**: X (Y versions total)
- **Active Evaluations**: X criteria
- **Sessions Logged**: X (last activity: date)
- **Datasets**: X (Y test cases total)
- **Test Runs**: X (last run: date)
- **Insights Generated**: X

## Critical Issues (if any)

1. {Issue}: {Impact and why it matters}

## Recommendations

### Priority 1: {Category}
- {Specific action}
- {Specific action}

### Priority 2: {Category}
- {Specific action}

## Next Steps

Based on this assessment, you should:
1. {First action with skill link if applicable}
2. {Second action}
3. {Third action}

---
*Use the `run-test` skill to execute tests after making changes*
*Use the `test-run-analysis` skill to analyze test results*
*Use the `dataset-management` skill to build or update datasets*
```

## Common Patterns and Recommendations

### Pattern: No Evaluation Criteria
**Symptom**: Completions or traces exist but no evaluation results
**Recommendation**:
1. Create at least 2-3 model-graded evaluations for your main template
2. Start with "bottoms-up" error conditions that act like unit tests: "citations present" or "accurate discount code format" or "includes suggested next action".
3. Enable insights generation on evaluation criteria

### Pattern: No Recent Test Runs
**Symptom**: Datasets exist but no test runs in 30+ days
**Recommendation**:
1. Run tests before any prompt changes using `/freeplay:run-test`
2. Set up comparative testing (baseline vs. new version)
3. Integrate testing into your development workflow

### Pattern: Orphaned Completions
**Symptom**: Completions not linked to prompt templates
**Recommendation**:
0. Make sure prompt templates exist, or help create them if not
1. Update SDK integration to include `prompt_template_id`
2. Link completions to environments for proper tracking
3. Review Freeplay SDK documentation for proper logging

### Pattern: Weak Dataset
**Symptom**: Only one dataset with limited test cases
**Recommendation**:
1. Ask the user to confirm the semantic meaning of the dataset (i.e. is it a "Golden Dataset" of representative input/output pairs, or "Failure Cases" including known failure to improve, or "Red Team" test cases that help detect abuse)
2. Analyze the existing test cases to understand what they cover
3. Analyze a sample of 100-200 recent production logs for the same component (prompt template or agent) and assess whether the dataset is representative of the production sample
4. Where production examples are markedly different or distinct, suggest examples to the user to add to their dataset. Always get confirmation from the user before changing the test cases in a dataset.

### Pattern: No Insights
**Symptom**: Insights list is empty despite activity
**Recommendation**:
1. Enable `enable_eval_insights` on project settings
2. Enable `enable_review_insights` on project settings
3. Ensure `generate_insights` is true on evaluation criteria
4. Wait for sufficient data (typically 50+ completions)

### Pattern: Evaluation Criteria Misalignment
**Symptom**: Insights show consistent mis-scoring or low pass rates on expected-good outputs
**Recommendation**:
1. Review evaluation criteria prompts for clarity
2. Check if criteria are inverted (high score = bad)
3. Validate model-graded evals against human judgment
4. Consider creating calibration datasets

## Security: Protecting API Keys in curl Commands

All curl commands in this skill MUST use process substitution to pass the
Authorization header, preventing the API key from appearing in process listings:

```bash
# CORRECT - key is not visible in `ps` output
curl -s "$FREEPLAY_BASE_URL/api/v2/..." \
     -H @<(echo "Authorization: Bearer $FREEPLAY_API_KEY")

# WRONG - key is exposed as a command-line argument
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/..."
```

Never log, echo, or display the value of FREEPLAY_API_KEY in output.

## Environment Variables

Required for API calls:
- `FREEPLAY_API_KEY`: Freeplay API key
- `FREEPLAY_BASE_URL`: API base URL (from .env file)

Project ID can come from:
- User specification
- `FREEPLAY_PROJECT_ID` environment variable
- MCP configuration

## Linking to Other Skills

After the health check, suggest relevant skills:
- **Missing tests?** → Use the `run-test` skill
- **Need to analyze results?** → Use the `test-run-analysis` skill
- **Need to build datasets?** → Use the `dataset-management` skill
- **Check deployments?** → Use the `get_deployed_prompt_versions` MCP tool
