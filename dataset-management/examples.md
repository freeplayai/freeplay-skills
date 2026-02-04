# Complete Workflow Examples

End-to-end examples with verification steps and checklists.

## Contents
- [Example 1: Create Prompt Dataset with Verification](#example-1-create-prompt-dataset-with-verification)
- [Example 2: Import Test Cases from CSV](#example-2-import-test-cases-from-csv)
- [Example 3: Create Agent Dataset for Multi-Turn Tests](#example-3-create-agent-dataset-for-multi-turn-tests)
- [Example 4: Update Multiple Test Cases](#example-4-update-multiple-test-cases)

---

## Example 1: Create Prompt Dataset with Verification

Complete workflow for creating a prompt dataset, adding test cases, and verifying the results.

### Workflow Checklist

Copy this checklist and check off as you progress:

```
Prompt Dataset Creation:
- [ ] Step 1: Set up environment and headers
- [ ] Step 2: Create dataset (verify 201 status)
- [ ] Step 3: Add test cases (verify 201 status)
- [ ] Step 4: Retrieve test cases to confirm count
- [ ] Step 5: Verify test case structure
```

### Implementation

```python
import requests
import os
import json

# Step 1: Setup
freeplay_api_key = os.environ["FREEPLAY_API_KEY"]
freeplay_api_base = os.environ["FREEPLAY_API_BASE"]
project_id = os.environ["FREEPLAY_PROJECT_ID"]

headers = {
    "Authorization": f"Bearer {freeplay_api_key}",
    "Content-Type": "application/json"
}
base = f"{freeplay_api_base}/api/v2/projects/{project_id}"

print("✓ Step 1: Environment configured")

# Step 2: Create dataset
print("\nStep 2: Creating dataset...")
dataset_response = requests.post(
    f"{base}/prompt-datasets",
    headers=headers,
    json={
        "name": "customer-support-golden-set",
        "description": "Golden test cases for customer support prompts",
        "input_names": ["question", "customer_tier"]
    }
)

if dataset_response.status_code != 201:
    print(f"✗ Error creating dataset: {dataset_response.status_code}")
    print(dataset_response.text)
    exit(1)

dataset = dataset_response.json()
dataset_id = dataset["id"]
print(f"✓ Step 2: Created dataset {dataset_id}")

# Step 3: Add test cases
print("\nStep 3: Adding test cases...")
test_cases = [
    {
        "inputs": {
            "question": "How do I track my order?",
            "customer_tier": "premium"
        },
        "output": "You can track your order by visiting your account dashboard...",
        "metadata": {"category": "shipping", "priority": "high"}
    },
    {
        "inputs": {
            "question": "What's your return policy?",
            "customer_tier": "standard"
        },
        "output": "Our return policy allows returns within 30 days...",
        "metadata": {"category": "returns", "priority": "high"}
    },
    {
        "inputs": {
            "question": "How do I upgrade my account?",
            "customer_tier": "standard"
        },
        "output": "You can upgrade to premium by visiting...",
        "metadata": {"category": "account", "priority": "medium"}
    }
]

cases_response = requests.post(
    f"{base}/prompt-datasets/{dataset_id}/test-cases/bulk",
    headers=headers,
    json={"data": test_cases}
)

if cases_response.status_code != 201:
    print(f"✗ Error adding test cases: {cases_response.status_code}")
    print(cases_response.text)
    exit(1)

result = cases_response.json()
print(f"✓ Step 3: Added {len(result['data'])} test cases")

# Step 4: Verify test case count
print("\nStep 4: Verifying test cases...")
verify_response = requests.get(
    f"{base}/prompt-datasets/{dataset_id}/test-cases",
    headers=headers
)

if verify_response.status_code != 200:
    print(f"✗ Error retrieving test cases: {verify_response.status_code}")
    exit(1)

all_cases = verify_response.json()
test_cases_list = all_cases.get('data', [])
expected_count = len(test_cases)
actual_count = len(test_cases_list)

if actual_count != expected_count:
    print(f"✗ Count mismatch: expected {expected_count}, got {actual_count}")
    exit(1)

print(f"✓ Step 4: Verified {actual_count} test cases")

# Step 5: Verify structure
print("\nStep 5: Verifying test case structure...")
sample = test_cases_list[0]
required_fields = ['id', 'inputs', 'output']
missing = [f for f in required_fields if f not in sample]

if missing:
    print(f"✗ Missing fields in test case: {missing}")
    exit(1)

print(f"✓ Step 5: Test case structure verified")
print(f"  Sample ID: {sample['id']}")
print(f"  Inputs: {list(sample['inputs'].keys())}")

print("\n" + "="*50)
print("✅ Dataset creation complete!")
print(f"Dataset ID: {dataset_id}")
print(f"Test cases: {actual_count}")
print("="*50)
```

---

## Example 2: Import Test Cases from CSV

Using the utility script to import large datasets from CSV files.

### Workflow Checklist

```
CSV Import Workflow:
- [ ] Step 1: Prepare CSV file with correct format
- [ ] Step 2: Verify CSV structure
- [ ] Step 3: Create target dataset
- [ ] Step 4: Run import script
- [ ] Step 5: Verify import completed successfully
```

### Step 1: Prepare CSV File

Create `test_cases.csv`:

```csv
inputs.question,inputs.customer_tier,output,category,priority
"How do I track my order?","premium","You can track your order...","shipping","high"
"What's your return policy?","standard","Our return policy...","returns","high"
"How do I reset my password?","standard","To reset your password...","account","medium"
"Can I cancel my order?","premium","Yes, you can cancel...","orders","high"
```

**Format rules:**
- Columns starting with `inputs.` become input fields
- `output` column becomes the expected output
- Other columns become metadata

### Step 2: Verify CSV Structure

```python
import csv

with open('test_cases.csv', 'r') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames

    print("CSV headers:", headers)

    # Check for required columns
    input_cols = [h for h in headers if h.startswith('inputs.')]
    has_output = 'output' in headers

    print(f"Input columns: {input_cols}")
    print(f"Has output column: {has_output}")

    # Count rows
    row_count = sum(1 for _ in reader)
    print(f"Total rows: {row_count}")
```

### Step 3: Create Target Dataset

```python
import requests
import os

headers = {
    "Authorization": f"Bearer {os.environ['FREEPLAY_API_KEY']}",
    "Content-Type": "application/json"
}
base = f"{os.environ['FREEPLAY_API_BASE']}/api/v2/projects/{os.environ['FREEPLAY_PROJECT_ID']}"

response = requests.post(
    f"{base}/prompt-datasets",
    headers=headers,
    json={
        "name": "imported-test-cases",
        "description": "Test cases imported from CSV",
        "input_names": ["question", "customer_tier"]
    }
)

dataset_id = response.json()["id"]
print(f"Created dataset: {dataset_id}")
```

### Step 4: Run Import Script

```bash
python scripts/import_testcases.py \
  --file test_cases.csv \
  --dataset-id ds_abc123 \
  --type prompt
```

Expected output:
```
Loading test cases from test_cases.csv...
✓ Loaded 4 test cases

Uploading to prompt-datasets/ds_abc123...
✓ Batch 1/1: Uploaded 4 test cases

==================================================
Upload complete: 4/4 test cases uploaded
Successful batches: 1/1
```

### Step 5: Verify Import

```python
response = requests.get(
    f"{base}/prompt-datasets/{dataset_id}/test-cases",
    headers=headers
)

test_cases = response.json().get('data', [])
print(f"✓ Verified: {len(test_cases)} test cases in dataset")

# Check a sample
if test_cases:
    sample = test_cases[0]
    print(f"Sample test case:")
    print(f"  Inputs: {sample['inputs']}")
    print(f"  Metadata: {sample.get('metadata', {})}")
```

---

## Example 3: Create Agent Dataset for Multi-Turn Tests

Creating an agent dataset with conversation history.

### Workflow Checklist

```
Agent Dataset with History:
- [ ] Step 1: Create agent dataset
- [ ] Step 2: Prepare test cases with history
- [ ] Step 3: Add test cases
- [ ] Step 4: Verify history structure
```

### Implementation

```python
import requests
import os

# Setup (same as previous examples)
headers = {
    "Authorization": f"Bearer {os.environ['FREEPLAY_API_KEY']}",
    "Content-Type": "application/json"
}
base = f"{os.environ['FREEPLAY_API_BASE']}/api/v2/projects/{os.environ['FREEPLAY_PROJECT_ID']}"

# Step 1: Create agent dataset
print("Step 1: Creating agent dataset...")
response = requests.post(
    f"{base}/agent-datasets",
    headers=headers,
    json={
        "name": "support-agent-scenarios",
        "description": "Multi-turn conversation tests for support agent"
    }
)

dataset_id = response.json()["id"]
print(f"✓ Created dataset: {dataset_id}")

# Step 2: Prepare test cases with history
print("\nStep 2: Preparing test cases...")
test_cases = [
    {
        "inputs": {
            "user_message": "I want to return an item from my order"
        },
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"},
            {"role": "user", "content": "I have a question about my order"},
            {"role": "assistant", "content": "I'd be happy to help. What's your order number?"},
            {"role": "user", "content": "Order #12345"}
        ],
        "output": "I can help you return an item from order #12345. Which item would you like to return?",
        "metadata": {
            "scenario": "return_request",
            "expected_tools": ["get_order", "initiate_return"],
            "complexity": "medium",
            "turns": 6
        }
    },
    {
        "inputs": {
            "user_message": "Where is my package?"
        },
        "history": [],  # Single-turn scenario
        "output": "I can help you track your package. What's your order number?",
        "metadata": {
            "scenario": "tracking_inquiry",
            "expected_tools": ["request_order_number"],
            "complexity": "low",
            "turns": 1
        }
    }
]

# Step 3: Add test cases
print("\nStep 3: Adding test cases...")
response = requests.post(
    f"{base}/agent-datasets/{dataset_id}/test-cases/bulk",
    headers=headers,
    json={"data": test_cases}
)

if response.status_code == 201:
    result = response.json()
    print(f"✓ Added {len(result['data'])} test cases")
else:
    print(f"✗ Error: {response.status_code} - {response.text}")
    exit(1)

# Step 4: Verify history structure
print("\nStep 4: Verifying test case structure...")
response = requests.get(
    f"{base}/agent-datasets/{dataset_id}/test-cases",
    headers=headers
)

test_cases_list = response.json().get('data', [])
for i, tc in enumerate(test_cases_list):
    history = tc.get('history', [])
    print(f"  Test case {i+1}: {len(history)} history turns")
    if history:
        print(f"    First turn: {history[0]['role']} - {history[0]['content'][:50]}...")

print("\n✅ Agent dataset with history created successfully!")
```

---

## Example 4: Update Multiple Test Cases

Batch updating test cases based on criteria.

### Workflow Checklist

```
Batch Update Workflow:
- [ ] Step 1: Retrieve all test cases
- [ ] Step 2: Filter test cases to update
- [ ] Step 3: Update each test case
- [ ] Step 4: Verify updates applied
```

### Implementation

```python
import requests
import os

# Setup
headers = {
    "Authorization": f"Bearer {os.environ['FREEPLAY_API_KEY']}",
    "Content-Type": "application/json"
}
base = f"{os.environ['FREEPLAY_API_BASE']}/api/v2/projects/{os.environ['FREEPLAY_PROJECT_ID']}"
dataset_id = "ds_abc123"  # Replace with your dataset ID

# Step 1: Retrieve all test cases
print("Step 1: Retrieving test cases...")
response = requests.get(
    f"{base}/prompt-datasets/{dataset_id}/test-cases",
    headers=headers
)

test_cases = response.json().get('data', [])
print(f"✓ Retrieved {len(test_cases)} test cases")

# Step 2: Filter test cases (e.g., category="shipping")
print("\nStep 2: Filtering test cases...")
to_update = [
    tc for tc in test_cases
    if tc.get('metadata', {}).get('category') == 'shipping'
]
print(f"✓ Found {len(to_update)} test cases to update")

# Step 3: Update each test case
print("\nStep 3: Updating test cases...")
updated_count = 0

for tc in to_update:
    # Add a new metadata field
    updated_metadata = tc.get('metadata', {})
    updated_metadata['updated'] = True
    updated_metadata['priority'] = 'critical'  # Upgrade priority

    response = requests.patch(
        f"{base}/prompt-datasets/{dataset_id}/test-cases/{tc['id']}",
        headers=headers,
        json={"metadata": updated_metadata}
    )

    if response.status_code == 200:
        updated_count += 1
        print(f"  ✓ Updated test case {tc['id']}")
    else:
        print(f"  ✗ Failed to update {tc['id']}: {response.status_code}")

print(f"\n✓ Step 3: Updated {updated_count}/{len(to_update)} test cases")

# Step 4: Verify updates
print("\nStep 4: Verifying updates...")
response = requests.get(
    f"{base}/prompt-datasets/{dataset_id}/test-cases",
    headers=headers
)

updated_cases = response.json().get('data', [])
verified = sum(
    1 for tc in updated_cases
    if tc.get('metadata', {}).get('category') == 'shipping'
    and tc.get('metadata', {}).get('updated') == True
)

print(f"✓ Verified {verified} test cases have new metadata")

if verified == len(to_update):
    print("\n✅ All updates verified successfully!")
else:
    print(f"\n⚠️  Warning: Expected {len(to_update)} updates, verified {verified}")
```

---

## Tips for All Workflows

1. **Always verify status codes:** Check for `201` on creates, `200` on reads/updates/deletes
2. **Include verification steps:** Don't assume operations succeeded
3. **Use descriptive variable names:** Makes debugging easier
4. **Log progress:** Print checkpoints as you go
5. **Handle errors explicitly:** Exit or retry on failures
6. **Count and compare:** Verify expected vs actual counts
7. **Sample verification:** Check structure of at least one item
8. **Use environment variables:** Never hardcode credentials
