# Ongoing Freeplay Tools

MCP tools for optimization and insights after initial integration.

## Prompt Optimization

**Tool:** `mcp__freeplay-mcp-v1__optimize_prompt`

Analyzes prompts against human labels, customer feedback, and best practices from logged completions. Generates improved prompt versions.

Parameters: `project_id`, `prompt_template_version_id`, `dataset_id`, plus optional flags for `use_best_practices`, `use_labels`, `use_customer_feedback`, `run_test_after_optimization`, and `user_instructions`.

## Insights Discovery

**Tool:** `mcp__freeplay-mcp-v1__list_insights`

Returns AI-generated insights about LLM usage: performance patterns, failure modes, usage trends, and optimization opportunities.

Parameters: `project_id`, optional `prompt_template_id`, `page`, `page_size`.

## Suggested Timeline

- **After 1 week:** Analyze common queries, ensure all fields logged
- **After 1 month:** Discover optimization opportunities, create datasets, optimize prompts
- **Ongoing:** Run logging quality checks weekly, review insights monthly, re-optimize quarterly
