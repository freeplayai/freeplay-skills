---
name: dataset-management
description: Create, manage, and curate Freeplay datasets (prompt-level and agent-level). Use when the user wants to create a new dataset, add test cases, update datasets, manage dataset content, import test data from CSV or JSONL, create golden sets, or build evaluation datasets.
---

# Freeplay Dataset Management

Manage test datasets for evaluating prompts and agents in Freeplay.

## Critical: Two Dataset Types

Freeplay has **two distinct dataset types** with **different API endpoints**:

1. **Prompt Datasets** - Test individual prompt templates → See [prompt-datasets.md](prompt-datasets.md)
2. **Agent Datasets** - Test complete agent workflows → See [agent-datasets.md](agent-datasets.md)

**ALWAYS confirm which type the user needs.** The APIs are not interchangeable.

**Quick decision guide:**
- User mentions "prompt", "template", or "component" → Prompt Dataset
- User mentions "agent", "workflow", or "end-to-end" → Agent Dataset

## Quick Start

### Setup (required for all operations)

```python
import requests
import os

headers = {
    "Authorization": f"Bearer {os.environ['FREEPLAY_API_KEY']}",
    "Content-Type": "application/json"
}
base = f"{os.environ['FREEPLAY_API_BASE']}/api/v2/projects/{os.environ['FREEPLAY_PROJECT_ID']}"
```

All examples assume this setup. Required environment variables:
- `FREEPLAY_API_KEY` - Your Freeplay API key
- `FREEPLAY_API_BASE` - API URL (e.g., https://api.freeplay.ai)
- `FREEPLAY_PROJECT_ID` - Target project ID

### Create a Prompt Dataset

```python
response = requests.post(
    f"{base}/prompt-datasets",
    headers=headers,
    json={
        "name": "my-golden-set",
        "description": "Golden test cases",
        "input_names": ["question", "context"]
    }
)
dataset_id = response.json()["id"]  # Status: 201 Created
```

### Create an Agent Dataset

```python
response = requests.post(
    f"{base}/agent-datasets",
    headers=headers,
    json={
        "name": "my-agent-tests",
        "description": "Agent workflow test cases"
    }
)
dataset_id = response.json()["id"]  # Status: 201 Created
```

### Add Test Cases (both types)

```python
# For prompt datasets: /prompt-datasets/{id}/test-cases/bulk
# For agent datasets: /agent-datasets/{id}/test-cases/bulk

test_cases = [
    {
        "inputs": {"question": "What is your refund policy?"},
        "output": "Expected response...",
        "metadata": {"category": "refunds"}
    }
]

response = requests.post(
    f"{base}/prompt-datasets/{dataset_id}/test-cases/bulk",
    headers=headers,
    json={"data": test_cases}  # Key is "data", not "test_cases"
)
# Status: 201 Created, max 100 items per request
```

## Common Operations

### Import from CSV/JSONL

Use the utility script for bulk imports:

```bash
python scripts/import_testcases.py \
  --file test_cases.csv \
  --dataset-id ds_abc123 \
  --type prompt  # or "agent"
```

Handles batching automatically (100 per request). See script help for full options:
```bash
python scripts/import_testcases.py --help
```

**CSV format:**
- Columns starting with `inputs.` become input fields
- `output` column becomes expected output
- Other columns become metadata

Example:
```csv
inputs.question,inputs.context,output,category,priority
"What is...","User context","Expected...","refunds","high"
```

### List Datasets

```python
# Prompt datasets
response = requests.get(f"{base}/prompt-datasets", headers=headers)
datasets = response.json().get('data', [])

# Agent datasets
response = requests.get(f"{base}/agent-datasets", headers=headers)
datasets = response.json().get('data', [])
```

### Get Test Cases

```python
# Replace prompt-datasets with agent-datasets for agent datasets
response = requests.get(
    f"{base}/prompt-datasets/{dataset_id}/test-cases",
    headers=headers
)
test_cases = response.json().get('data', [])
```

### Update Test Case

```python
response = requests.patch(
    f"{base}/prompt-datasets/{dataset_id}/test-cases/{test_case_id}",
    headers=headers,
    json={
        "inputs": {"question": "Updated question"},
        "output": "Updated output",
        "metadata": {"updated": True}
    }
)
# Status: 200 OK
```

### Delete Test Cases

```python
response = requests.delete(
    f"{base}/prompt-datasets/{dataset_id}/test-cases/bulk",
    headers=headers,
    json={"test_case_ids": ["tc_123", "tc_456"]}  # Max 100 per request
)
# Status: 200 OK
```

## Workflow Patterns

For complex operations, use the checklist pattern:

```
Dataset Creation with Verification:
- [ ] Step 1: Create dataset (verify 201 status)
- [ ] Step 2: Add test cases (verify 201 status)
- [ ] Step 3: Retrieve test cases to confirm count
- [ ] Step 4: Verify test case structure
```

See [examples.md](examples.md) for complete workflows with verification steps.

## Reference Documentation

**Complete API references:**
- [prompt-datasets.md](prompt-datasets.md) - All prompt dataset operations
- [agent-datasets.md](agent-datasets.md) - All agent dataset operations
- [examples.md](examples.md) - Complete workflow examples with verification

**Quick links by task:**
- Creating datasets: [Prompt](prompt-datasets.md#creating-datasets) | [Agent](agent-datasets.md#creating-datasets)
- Adding test cases: [Prompt](prompt-datasets.md#adding-test-cases) | [Agent](agent-datasets.md#adding-test-cases)
- Test case structure: [Prompt](prompt-datasets.md#test-case-structure) | [Agent](agent-datasets.md#test-case-structure)
- Updating operations: [Prompt](prompt-datasets.md#updating-test-cases) | [Agent](agent-datasets.md#updating-test-cases)
- Deleting operations: [Prompt](prompt-datasets.md#deleting-test-cases) | [Agent](agent-datasets.md#deleting-test-cases)

## Utility Scripts

**`scripts/import_testcases.py`** - Import test cases from CSV or JSONL files
- Handles batching automatically (100 per request)
- Supports both prompt and agent datasets
- Provides progress reporting and error handling

**`scripts/batch_operations.py`** - Reusable batch operation functions
- Use in custom scripts for programmatic batch operations
- Functions: `batch_create_test_cases()`, `batch_delete_test_cases()`

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Path Not Found | Wrong endpoint path or dataset type | Verify `/api/v2/` base and correct type (`prompt-datasets` or `agent-datasets`) |
| Bulk limit exceeded | >100 items in single request | Use `scripts/import_testcases.py` or batch manually |
| Unauthorized | Invalid or missing API key | Check `FREEPLAY_API_KEY` environment variable |
| Incompatible test case | Input keys don't match prompt variables | Verify `inputs` keys match prompt template variables |

## Best Practices

1. **Verify operations:** Always check status codes and counts after operations
2. **Use descriptive names:** Dataset names should indicate purpose (e.g., "refunds-edge-cases")
3. **Include metadata:** Tag test cases for filtering (category, priority, source)
4. **Provide expected outputs:** Required for meaningful evaluations
5. **Batch large operations:** Use scripts for >10 items
6. **Organize by scenario:** Create focused datasets rather than one large dataset
7. **Match input names:** For prompt datasets, ensure inputs match template variables

## Related Skills

After creating datasets:
- Run tests using the `run-test` skill
- Analyze results using the `test-run-analysis` skill
- Deploy prompts using prompt deployment skills

## Freeplay Documentation

- [Datasets Overview](https://docs.freeplay.ai/core-concepts/datasets/datasets)
- [Dataset Curation](https://docs.freeplay.ai/core-concepts/datasets/dataset-curation)
- [Component-Level Testing](https://docs.freeplay.ai/core-concepts/test-runs/component-level-test-runs)
- [End-to-End Testing](https://docs.freeplay.ai/core-concepts/test-runs/end-to-end-test-runs)
