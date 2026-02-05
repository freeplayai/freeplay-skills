---
name: run-test
description: Execute Freeplay test runs to evaluate AI features. Use when the user wants to run a test, execute tests against a dataset, or trigger a test run for their prompts or agents.
---

# Run Freeplay Test

This skill helps users execute Freeplay test runs via the SDK/API to evaluate their AI features against datasets.

**Note:** This skill is for SDK/API-based test runs only, not UI-based testing from the Freeplay dashboard.

## When to use this skill

- "Run a test for my prompt"
- "Execute the test run for customer support"
- "Test my agent against the golden dataset"
- "Run evaluation tests"
- "Kick off a test run"
- "I want to test my prompt changes"

## Workflow

### Step 1: Identify the Test Run Code Path

Search the codebase for existing test run implementation. Look for:

```bash
# Search patterns (run these to find test run implementations)
grep -r "test_runs.create" --include="*.py" .
grep -r "fp_client.test_runs" --include="*.py" .
grep -r "freeplay.*test" --include="*.py" .
grep -r "TestRun" --include="*.py" .
```

The key API call to look for is:

**Python SDK:**
```python
test_run = fp_client.test_runs.create(
    project_id=project_id,
    testlist="Dataset Name",
    name="Test Run Name"
)
```

**TypeScript SDK:**
```typescript
const testRun = await fpClient.testRuns.create({
    projectId: projectId,
    testlist: "Dataset Name",
    name: "Test Run Name"
});
```

### Step 2: If No Test Run Code Exists

If the search returns no results, inform the user:

> I couldn't find an existing test run script in your codebase. To run Freeplay test runs, you'll need to set up a test runner script first.
>
> **Documentation to get started:**
> - [Test Runs Overview](https://docs.freeplay.ai/core-concepts/test-runs/test-runs)
> - [Component-Level Testing](https://docs.freeplay.ai/core-concepts/test-runs/component-level-test-runs) - For testing individual prompts
> - [End-to-End Testing](https://docs.freeplay.ai/core-concepts/test-runs/end-to-end-test-runs) - For testing complete workflows/agents
>
> Would you like me to help you understand what's needed to set up a test runner?

**Do NOT attempt to write the test runner for them.** This requires understanding their specific:
- Pipeline architecture
- Dataset structure
- Evaluation criteria
- Environment configuration

### Step 3: If Test Run Code Exists

Once you've found the test run implementation:

1. **Identify the entry point** - Find the script/function that initiates test runs
2. **Check for required environment variables:**
   - `FREEPLAY_API_KEY`
   - `FREEPLAY_API_BASE` or `FREEPLAY_API_URL`
   - `FREEPLAY_PROJECT_ID`
   - `OPENAI_API_KEY` (or other LLM provider keys)

3. **Determine how to run it:**
   ```bash
   # Common patterns
   python run_tests.py
   python -m tests.run_freeplay_tests
   npm run test:freeplay
   pytest tests/test_freeplay.py
   ```

4. **Ask the user for any required parameters:**
   - Dataset/testlist name
   - Test run name
   - Prompt template to test
   - Environment (if applicable)

### Step 4: Execute with Consent

Before running, confirm with the user:

> I found the test runner at `[path]`. This will:
> - Run tests against the `[dataset]` dataset
> - Test the `[prompt/agent]`
> - Make API calls to Freeplay and your LLM provider
>
> Ready to execute?

Only proceed with explicit consent.

### Step 5: Handle Results

**On Success:**
- Report the test run completed
- Provide the test run ID for reviewing results
- Share any immediate metrics if available in output
- **Always suggest using the `test-run-analysis` skill** to analyze results and suggest improvements to the prompt or agent based on evaluation metrics

**On Failure:**
- Capture the error output
- Identify common issues:
  - Missing environment variables
  - Invalid API keys
  - Dataset not found
  - Network/connectivity issues
  - Rate limiting
- Help debug with the user

## Example Test Run Script Structure

For reference, a typical component-level test run script looks like:

```python
from freeplay import Freeplay, RecordPayload
from openai import OpenAI
import os
from scripts.secrets import SecretString

# Initialize clients (use SecretString to prevent accidental logging)
api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))
fp_client = Freeplay(
    api_key=api_key.get(),
    api_base=os.environ["FREEPLAY_API_BASE"]
)
openai_client = OpenAI()

project_id = os.environ["FREEPLAY_PROJECT_ID"]

# Create test run
test_run = fp_client.test_runs.create(
    project_id=project_id,
    testlist="Golden Set",
    name="My Test Run"
)

# Get prompt template
template_prompt = fp_client.prompts.get(
    project_id=project_id,
    template_name="my-prompt",
    environment="latest"
)

# Process each test case
for test_case in test_run.test_cases:
    formatted_prompt = template_prompt.bind(test_case.variables).format()

    # Call LLM
    response = openai_client.chat.completions.create(
        model=formatted_prompt.prompt_info.model,
        messages=formatted_prompt.llm_prompt,
        **formatted_prompt.prompt_info.model_parameters
    )

    # Record results back to Freeplay
    fp_client.recordings.create(RecordPayload(
        # ... recording configuration
    ))

print(f"Test run completed: {test_run.id}")
```

## Environment Variables

Required variables that must be set:
- `FREEPLAY_API_KEY` - Freeplay API key
- `FREEPLAY_API_BASE` - Freeplay API URL (e.g., https://api.freeplay.ai)
- `FREEPLAY_PROJECT_ID` - Project ID in Freeplay
- LLM provider keys (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)

## Tips

- Always search the codebase first before assuming no test runner exists
- Check common locations: `scripts/`, `tests/`, `tools/`, root directory
- Look for files named: `run_test*.py`, `test_runner.py`, `freeplay_test*.py`
- Check `package.json` scripts or `pyproject.toml` for test commands
- Environment variables may be in `.env`, `.env.local`, or CI configuration
