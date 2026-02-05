# Prompt Dataset Operations

Complete reference for managing prompt-level datasets in Freeplay.

## Contents
- [Creating Datasets](#creating-datasets)
- [Adding Test Cases](#adding-test-cases)
- [Listing Datasets](#listing-datasets)
- [Retrieving Test Cases](#retrieving-test-cases)
- [Updating Test Cases](#updating-test-cases)
- [Updating Dataset Metadata](#updating-dataset-metadata)
- [Test Case Structure](#test-case-structure)

## Important Safety Note

**No Deletion Operations:** This skill does NOT support deletion operations (deleting datasets or test cases). If deletion is needed, it must be performed manually through the Freeplay UI or API directly.

**Confirmation Required:** Always ask for user confirmation before performing any write operations (creating datasets, adding test cases, updating datasets or test cases).

## Setup

All operations assume this setup (shown in SKILL.md):

```python
import requests
import os
from scripts.secrets import SecretString

api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))
headers = {
    "Authorization": f"Bearer {api_key.get()}",
    "Content-Type": "application/json"
}
base = f"{os.environ.get('FREEPLAY_BASE_URL', 'https://app.freeplay.ai')}/api/v2/projects/{os.environ['FREEPLAY_PROJECT_ID']}"
```

## Creating Datasets

**Endpoint:** `POST /api/v2/projects/{project_id}/prompt-datasets`

**Required fields:**
- `name` - Unique identifier for the dataset

**Optional fields:**
- `description` - Human-readable description
- `input_names` - Array of input field names (e.g., `["question", "context"]`)
- `media_input_names` - Array of media input field names
- `support_history` - Boolean, whether dataset supports conversation history (default: false)

**Example:**

```python
response = requests.post(
    f"{base}/prompt-datasets",
    headers=headers,
    json={
        "name": "customer-support-golden-set",
        "description": "Golden test cases for customer support prompt",
        "input_names": ["question", "customer_tier"],
        "support_history": False
    }
)

if response.status_code == 201:
    dataset = response.json()
    dataset_id = dataset["id"]
    print(f"Created dataset: {dataset_id}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `201 Created` on success with dataset object

## Adding Test Cases

**Endpoint:** `POST /api/v2/projects/{project_id}/prompt-datasets/{dataset_id}/test-cases/bulk`

**Request body:**
```json
{
  "data": [
    {
      "inputs": {"key": "value", ...},
      "output": "Expected response",
      "metadata": {"custom": "data"}
    }
  ]
}
```

**Important:** Request key is `"data"`, not `"test_cases"`

**Example:**

```python
test_cases = [
    {
        "inputs": {
            "question": "What is your refund policy?",
            "customer_tier": "premium"
        },
        "output": "Our refund policy allows returns within 30 days...",
        "metadata": {
            "category": "refunds",
            "priority": "high"
        }
    },
    {
        "inputs": {
            "question": "How do I reset my password?",
            "customer_tier": "standard"
        },
        "output": "To reset your password, visit...",
        "metadata": {
            "category": "account",
            "priority": "medium"
        }
    }
]

response = requests.post(
    f"{base}/prompt-datasets/{dataset_id}/test-cases/bulk",
    headers=headers,
    json={"data": test_cases}
)

if response.status_code == 201:
    result = response.json()
    print(f"Created {len(result['data'])} test cases")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Limits:**
- Maximum 100 test cases per request
- For larger imports, use `scripts/import_testcases.py`

**Response:** `201 Created` with created test cases in `data` array

## Listing Datasets

**Endpoint:** `GET /api/v2/projects/{project_id}/prompt-datasets`

**Example:**

```python
response = requests.get(f"{base}/prompt-datasets", headers=headers)

if response.status_code == 200:
    result = response.json()
    datasets = result.get('data', [])
    print(f"Found {len(datasets)} prompt datasets")
    for ds in datasets:
        print(f"  - {ds['name']} (ID: {ds['id']})")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `200 OK` with datasets array in `data` field

## Retrieving Test Cases

**Endpoint:** `GET /api/v2/projects/{project_id}/prompt-datasets/{dataset_id}/test-cases`

**Example:**

```python
response = requests.get(
    f"{base}/prompt-datasets/{dataset_id}/test-cases",
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    test_cases = result.get('data', [])
    print(f"Found {len(test_cases)} test cases")
    for tc in test_cases:
        print(f"  - ID: {tc['id']}")
        print(f"    Inputs: {tc['inputs']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `200 OK` with test cases array in `data` field

## Updating Test Cases

**Endpoint:** `PATCH /api/v2/projects/{project_id}/prompt-datasets/{dataset_id}/test-cases/{test_case_id}`

**Example:**

```python
response = requests.patch(
    f"{base}/prompt-datasets/{dataset_id}/test-cases/{test_case_id}",
    headers=headers,
    json={
        "inputs": {"question": "Updated question"},
        "output": "Updated expected output",
        "metadata": {"updated": True}
    }
)

if response.status_code == 200:
    updated = response.json()
    print("Test case updated successfully")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `200 OK` with updated test case object

## Updating Dataset Metadata

**Endpoint:** `PATCH /api/v2/projects/{project_id}/prompt-datasets/{dataset_id}`

**Example:**

```python
response = requests.patch(
    f"{base}/prompt-datasets/{dataset_id}",
    headers=headers,
    json={
        "name": "updated-name",
        "description": "Updated description",
        "input_names": ["question", "context", "user_id"]
    }
)

if response.status_code == 200:
    print("Dataset updated successfully")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `200 OK` with updated dataset object

## Test Case Structure

### Basic Structure

```json
{
  "inputs": {
    "variable_name": "value",
    "another_variable": "value"
  },
  "output": "Expected LLM response (optional)",
  "metadata": {
    "category": "tag",
    "source": "production",
    "priority": "high"
  }
}
```

### Field Details

**`inputs` (required):**
- Object containing input variables for the prompt
- Keys must match prompt template variable names
- At least one key must match for compatibility with a prompt

**`output` (optional but recommended):**
- Expected response from the LLM
- Used for evaluation and comparison
- Can be a string or structured output

**`metadata` (optional):**
- Flexible object for custom categorization
- Useful for filtering and organizing test cases
- Common fields: `category`, `source`, `priority`, `tags`

### Examples

**Simple test case:**
```json
{
  "inputs": {
    "question": "What are your shipping options?"
  },
  "output": "We offer standard (5-7 days) and express (2-3 days) shipping.",
  "metadata": {
    "category": "shipping"
  }
}
```

**Multi-input test case:**
```json
{
  "inputs": {
    "question": "Can I return this item?",
    "customer_tier": "premium",
    "purchase_date": "2024-01-15"
  },
  "output": "Yes, as a premium customer you have 60 days to return items.",
  "metadata": {
    "category": "returns",
    "priority": "high",
    "edge_case": false
  }
}
```

## Best Practices

1. **Match input names:** Ensure `inputs` keys match your prompt template variable names
2. **Include outputs:** Always provide expected outputs for meaningful evaluations
3. **Use metadata:** Tag test cases for easy filtering (e.g., by category, priority, source)
4. **Batch operations:** Use bulk endpoints and scripts for operations >10 items
5. **Verify after upload:** Always check test case count after bulk uploads
6. **Descriptive names:** Use clear dataset names that indicate purpose (e.g., "refunds-edge-cases")
