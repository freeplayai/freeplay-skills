# Dataset Management Scripts

Utility scripts for batch operations on Freeplay datasets.

## import_testcases.py

Import test cases from CSV or JSONL files into Freeplay datasets.

### Usage

```bash
python import_testcases.py \
  --file <path-to-file> \
  --dataset-id <dataset-id> \
  --type <prompt|agent> \
  [--batch-size <num>]
```

### Arguments

- `--file` (required) - Path to CSV or JSONL file
- `--dataset-id` (required) - Freeplay dataset ID
- `--type` (required) - Dataset type: `prompt` or `agent`
- `--batch-size` (optional) - Items per batch (1-100, default: 100)

### CSV Format

Columns starting with `inputs.` become input fields:

```csv
inputs.question,inputs.context,output,category,priority
"What is...","User context","Expected...","refunds","high"
```

### JSONL Format

One test case per line:

```jsonl
{"inputs": {"question": "What is..."}, "output": "Expected...", "metadata": {"category": "refunds"}}
{"inputs": {"question": "How do I..."}, "output": "You can...", "metadata": {"category": "account"}}
```

### Environment Variables

Required:
- `FREEPLAY_API_KEY` - Your Freeplay API key
- `FREEPLAY_BASE_URL` - API URL (default: https://app.freeplay.ai)
- `FREEPLAY_PROJECT_ID` - Target project ID

### Example

```bash
export FREEPLAY_API_KEY="fp_..."
export FREEPLAY_BASE_URL="https://app.freeplay.ai"
export FREEPLAY_PROJECT_ID="proj_123"

python scripts/import_testcases.py \
  --file my_test_cases.csv \
  --dataset-id ds_abc123 \
  --type prompt
```

## batch_operations.py

Reusable functions for batch operations in custom scripts.

### Usage

Import functions in your Python scripts:

```python
from batch_operations import batch_create_test_cases

# Create test cases in batches
test_cases = [...]
count = batch_create_test_cases(
    test_cases=test_cases,
    dataset_type="prompt-datasets",
    dataset_id="ds_abc123",
    batch_size=100,
    verbose=True
)
```

### Functions

**`get_freeplay_config()`** - Get config from environment variables

**`get_headers(api_key)`** - Get standard API request headers

**`batch_create_test_cases(test_cases, dataset_type, dataset_id, batch_size=100, verbose=True)`**
- Uploads test cases in batches
- Returns count of successfully created test cases

### Environment Variables

Same as `import_testcases.py`:
- `FREEPLAY_API_KEY`
- `FREEPLAY_BASE_URL`
- `FREEPLAY_PROJECT_ID`

### Note

Deletion operations are not supported through this skill. If you need to delete test cases or datasets, do so manually through the Freeplay UI or API directly.
