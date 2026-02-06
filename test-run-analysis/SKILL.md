---
name: test-run-analysis
description: Analyze Freeplay test run results to surface insights, evaluation metrics, and test case details. Use when the user wants to review test run performance, compare two test runs, understand evaluation scores, or identify failing test cases. Do NOT use for executing new test runs (use run-test) or managing datasets (use dataset-management).
---

# Test Run Analysis

This skill helps you review Freeplay test run results, view evaluation metrics, and identify patterns across test cases.

## When to use this skill

- "Summarize the results of test run X"
- "Summarize the major differences between two test runs in the same comparison"
- "What were the metrics for my last test run?"
- "Analyze test run [ID]"
- "Which test cases failed in run X?"
- "What are the evaluation scores from this test?"
- User mentions a specific test run ID and wants insights
- Compare two test runs and summarize differences between latency, cost, and evaluations
- Select a winner from two test runs based on available data

## Available API Endpoints

### Get Test Run Summary
**Endpoint:** `GET /api/v2/projects/{project_id}/test-runs/id/{test_run_id}`

Returns:
```json
{
  "id": "test-run-uuid",
  "name": "Test run name",
  "description": "Description",
  "created_at": 1234567890,
  "prompt_name": "Prompt template name",
  "prompt_version": "version-id",
  "model_name": "gpt-4",
  "sessions_count": 10,
  "summary_statistics": {
    "human_evaluation": {},
    "auto_evaluation": {
      "criteria_name": {
        "pass": 8,
        "fail": 2,
        "average_score": 0.85
      }
    },
    "client_evaluation": {}
  }
}
```

### List All Test Runs
**Endpoint:** `GET /api/v2/projects/{project_id}/test-runs`

Returns a list of all test runs with their IDs and associated test case IDs.

## How to Analyze a Test Run

When a user provides a test run ID, follow these steps:

### 1. Fetch Test Run Summary
Use curl or Python to call the API:

```bash
curl -H "Authorization: Bearer $FREEPLAY_API_KEY" \
     "$FREEPLAY_BASE_URL/api/v2/projects/{project_id}/test-runs/id/{test_run_id}"
```

### 2. Extract Key Insights

From the response, identify:
- **Overall performance:** sessions_count, average scores
- **Evaluation metrics:** Parse the `summary_statistics` object
  - `auto_evaluation`: LLM-as-judge metrics
  - `human_evaluation`: Human review scores
  - `client_evaluation`: Custom evaluation criteria
- **Prompt details:** prompt_name, prompt_version, model_name
- **Timestamp:** created_at (Unix timestamp)

### 3. Analyze Metrics

For each evaluation criterion in `summary_statistics`:
- Count pass/fail cases
- Calculate pass rate percentage
- Identify average scores
- Flag criteria with low performance

## Environment Variables Required

The following environment variables must be set:
- `FREEPLAY_API_KEY`: Your Freeplay API key
- `FREEPLAY_BASE_URL`: Freeplay API base URL (default: https://app.freeplay.ai)

These are typically configured in the plugin's `.mcp.json` file or user's environment.

Project ID can come from:
- User specification
- MCP `list_projects()` tool to discover available projects

## Response Format

When presenting test run results to the user, include:

1. **Summary Header**
   - Test run name
   - Prompt tested & version
   - Model used
   - Number of test cases
   - Date/time

2. **Evaluation Metrics**
   - For each criterion:
     - Criterion name
     - Pass/fail count
     - Pass rate percentage
     - Average score (if applicable)

3. **Key Insights**
   - Overall pass rate
   - Best performing criteria
   - Areas needing improvement
   - Any notable patterns or failures

4. **Recommendations**
   - Suggest next steps based on results
   - Highlight specific test cases to review if pass rate is low
   - **When no evaluations are configured:** The test run completed but has no quantitative metrics to analyze. Provide specific, actionable guidance:
     - Explain that without evaluations, test runs only capture raw outputs — evaluations are what score those outputs automatically on each run
     - Direct the user to set up evaluations: open the prompt in the Freeplay UI → go to the **Evaluate** tab → create evaluation criteria (e.g., model-graded criteria that check for accuracy, relevance, tone, or format compliance)
     - Link to the documentation: [Evaluations Overview](https://docs.freeplay.ai/core-concepts/evaluations)
     - Suggest running the **health-check** skill (`/health-check`) to get a full assessment of their project setup, including evaluation coverage
     - For immediate value, recommend reviewing a sample of test case outputs directly in the Freeplay UI to manually spot-check quality before investing in automated evaluations

## Example Analysis Output

```
# Test Run: "New test"
- Prompt: Chat Transcript to Issue
- Model: gpt-4-turbo
- Test Cases: 15
- Date: Jan 30, 2025

## Evaluation Results

### Accuracy (auto_evaluation)
- Pass: 13/15 (86.7%)
- Average Score: 0.87

### Relevance (auto_evaluation)
- Pass: 14/15 (93.3%)
- Average Score: 0.92

### Format Compliance (auto_evaluation)
- Pass: 15/15 (100%)
- Average Score: 1.0

## Overall Performance
✓ Strong performance across all criteria
✓ 93.3% overall pass rate
⚠ Review 2 failing test cases for Accuracy criterion

## Recommendations
1. Investigate the 2 accuracy failures to identify patterns
2. Consider adding more test cases for edge cases
3. Prompt is ready for staging deployment
```


## Example Analysis Output (Multiple Test Runs)

```
# Test Run Comparison

## Test Run 1: "Bug Report Summarization"
- Prompt: Bug-to-Summary Converter
- Model: gpt-4-turbo
- Test Cases: 10
- Date: Jan 15, 2025

### Evaluation Results

#### Accuracy (auto_evaluation)
- Pass: 8/10 (80.0%)
- Average Score: 0.82

#### Clarity (manual_evaluation)
- Pass: 7/10 (70.0%)
- Average Score: 0.73

#### Format Compliance (auto_evaluation)
- Pass: 10/10 (100%)
- Average Score: 1.0

## Overall Performance
✓ Good accuracy and format compliance
⚠ Clarity underperforms at 70%
✓ 83.3% average pass rate

## Recommendations
1. Refine prompt instructions to improve clarity in summaries
2. Review the 3 test cases with clarity failures
3. Maintain strong format adherence

---

## Test Run 2: "Support Ticket Categorization 234dv vs a24bd"
- Prompt: Ticket Classifier
- Versions compared: 
    - Version: 234dv
      - Model: Opus 4.5
      - Created by: Prompt optimizer
      - Created: 10/11/25 11:12:32
    - Version: a24bd
      - Model: Sonnet 4.5
      - Created by: Rob Rhyne
      - Created: 10/10/25 11:12:32
- Test Cases: 12
- Date: Feb 2, 2025

### Evaluation Results

#### Accuracy (auto_evaluation)
- Pass: 9/12 (75.0%)
- Average Score: 0.79

#### Category Relevance (auto_evaluation)
- Pass: 8/12 (66.7%) ⚠
- Average Score: 0.68

#### Format Compliance (auto_evaluation)
- Pass: 11/12 (91.7%)
- Average Score: 0.95

## Overall Performance
⚠ Category relevance below 70% – needs attention
✓ Good format compliance, moderate accuracy
✗ 77.8% average pass rate

## Recommendations
1. Investigate category relevance failures—review misclassified tickets
2. Consider adding category examples to the prompt
3. Re-evaluate if accuracy improves after prompt update

```


## Tips

- Always format Unix timestamps into readable dates
- Calculate percentages and round to 1 decimal place
- Use visual indicators (✓ ⚠ ✗) for quick scanning
- Highlight concerning metrics (< 70% pass rate)
- Keep the analysis concise but actionable
