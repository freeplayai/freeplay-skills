# Agent Dataset Operations

Complete reference for managing agent-level datasets in Freeplay.

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
project_id = "<project-id>"  # Provided by user or discovered via list_projects()
base = f"{os.environ.get('FREEPLAY_BASE_URL', 'https://app.freeplay.ai')}/api/v2/projects/{project_id}"
```

## Creating Datasets

**Endpoint:** `POST /api/v2/projects/{project_id}/agent-datasets`

**Required fields:**
- `name` - Unique identifier for the dataset

**Optional fields:**
- `description` - Human-readable description
- `compatible_agent_ids` - List of agent IDs this dataset works with

**Example:**

```python
response = requests.post(
    f"{base}/agent-datasets",
    headers=headers,
    json={
        "name": "customer-agent-test-set",
        "description": "Test cases for customer support agent workflows",
        "compatible_agent_ids": ["agent_123", "agent_456"]
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

**Endpoint:** `POST /api/v2/projects/{project_id}/agent-datasets/{dataset_id}/test-cases/bulk`

**Request body:**
```json
{
  "data": [
    {
      "inputs": {"key": "value", ...},
      "output": "Expected response or trace",
      "history": [...],
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
            "user_message": "I need help with my order",
            "user_id": "user_123"
        },
        "output": "Expected agent final response",
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ],
        "metadata": {
            "scenario": "order_inquiry",
            "expected_tools": ["get_order", "check_status"],
            "complexity": "medium"
        }
    },
    {
        "inputs": {
            "user_message": "Cancel my subscription",
            "user_id": "user_456"
        },
        "output": "Expected agent workflow completion",
        "metadata": {
            "scenario": "cancellation",
            "expected_tools": ["get_subscription", "cancel_subscription"],
            "complexity": "high"
        }
    }
]

response = requests.post(
    f"{base}/agent-datasets/{dataset_id}/test-cases/bulk",
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

**Endpoint:** `GET /api/v2/projects/{project_id}/agent-datasets`

**Example:**

```python
response = requests.get(f"{base}/agent-datasets", headers=headers)

if response.status_code == 200:
    result = response.json()
    datasets = result.get('data', [])
    print(f"Found {len(datasets)} agent datasets")
    for ds in datasets:
        print(f"  - {ds['name']} (ID: {ds['id']})")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `200 OK` with datasets array in `data` field

## Retrieving Test Cases

**Endpoint:** `GET /api/v2/projects/{project_id}/agent-datasets/{dataset_id}/test-cases`

**Example:**

```python
response = requests.get(
    f"{base}/agent-datasets/{dataset_id}/test-cases",
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    test_cases = result.get('data', [])
    print(f"Found {len(test_cases)} test cases")
    for tc in test_cases:
        print(f"  - ID: {tc['id']}")
        print(f"    Scenario: {tc.get('metadata', {}).get('scenario', 'N/A')}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:** `200 OK` with test cases array in `data` field

## Updating Test Cases

**Endpoint:** `PATCH /api/v2/projects/{project_id}/agent-datasets/{dataset_id}/test-cases/{test_case_id}`

**Example:**

```python
response = requests.patch(
    f"{base}/agent-datasets/{dataset_id}/test-cases/{test_case_id}",
    headers=headers,
    json={
        "inputs": {"user_message": "Updated message"},
        "output": "Updated expected workflow result",
        "metadata": {"updated": True, "scenario": "updated_scenario"}
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

**Endpoint:** `PATCH /api/v2/projects/{project_id}/agent-datasets/{dataset_id}`

**Example:**

```python
response = requests.patch(
    f"{base}/agent-datasets/{dataset_id}",
    headers=headers,
    json={
        "name": "updated-agent-dataset",
        "description": "Updated description",
        "compatible_agent_ids": ["agent_123", "agent_789"]
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
    "user_message": "Initial user input",
    "context_variable": "value"
  },
  "output": "Expected final response or trace (optional)",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "metadata": {
    "scenario": "workflow_type",
    "expected_tools": ["tool1", "tool2"],
    "complexity": "high"
  }
}
```

### Field Details

**`inputs` (required):**
- Object containing initial variables for the agent
- Typically includes the user's message and context
- Keys should match agent input expectations

**`output` (optional but recommended):**
- Expected final response from the agent
- Can be the complete response text or expected trace structure
- Used for evaluation and comparison

**`history` (optional):**
- Array of previous conversation turns
- Each turn has `role` ("user" or "assistant") and `content`
- Provides conversation context for multi-turn scenarios

**`metadata` (optional):**
- Flexible object for custom categorization
- Useful for tracking scenarios, expected behavior, complexity
- Common fields: `scenario`, `expected_tools`, `complexity`, `edge_case`

### Examples

**Simple single-turn test:**
```json
{
  "inputs": {
    "user_message": "What's the status of my order?"
  },
  "output": "Your order #12345 is out for delivery and should arrive today.",
  "metadata": {
    "scenario": "order_status",
    "expected_tools": ["get_order_status"],
    "complexity": "low"
  }
}
```

**Multi-turn conversation test:**
```json
{
  "inputs": {
    "user_message": "I want to return an item"
  },
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help today?"},
    {"role": "user", "content": "I have a question about an order"},
    {"role": "assistant", "content": "I'd be happy to help with your order. What's your order number?"},
    {"role": "user", "content": "It's order #12345"}
  ],
  "output": "I can help you return items from order #12345. Which item would you like to return?",
  "metadata": {
    "scenario": "returns_multi_turn",
    "expected_tools": ["get_order", "initiate_return"],
    "complexity": "medium",
    "turns": 6
  }
}
```

**Complex workflow test:**
```json
{
  "inputs": {
    "user_message": "I was charged twice for my subscription",
    "user_id": "user_789"
  },
  "output": "I've identified the duplicate charge and issued a refund...",
  "metadata": {
    "scenario": "billing_issue_resolution",
    "expected_tools": [
      "get_user_subscriptions",
      "get_billing_history",
      "identify_duplicate_charge",
      "issue_refund",
      "send_confirmation_email"
    ],
    "complexity": "high",
    "requires_escalation": false
  }
}
```

## Best Practices

1. **Test realistic scenarios:** Include common user intents and edge cases
2. **Use conversation history:** For multi-turn tests, provide relevant history
3. **Document expected tools:** Use metadata to track which tools the agent should use
4. **Include complexity ratings:** Tag test cases by complexity for organized testing
5. **Batch operations:** Use bulk endpoints and scripts for operations >10 items
6. **Verify after upload:** Always check test case count after bulk uploads
7. **Descriptive names:** Use clear dataset names (e.g., "support-agent-edge-cases")
8. **Track scenarios:** Use consistent scenario names in metadata for filtering
