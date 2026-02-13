# Converting to Mustache for Freeplay

Freeplay uses Mustache templating for prompts. This guide explains how to convert from other templating systems and what Mustache supports.

**For message structure mapping** (determining roles, splitting messages, handling history), see `../_shared/prompt-mapping-guide.md`.

## Most Common Conversions (90% of cases)

- Python f-string `{var}` → Mustache `{{var}}`
- Jinja2 `{{ var }}` → Mustache `{{var}}` (remove spaces)
- JS template literal `${var}` → Mustache `{{var}}`
- History loop → `{"kind": "history"}` placeholder (NOT a variable)

Key rule: If it requires logic or computation, move it to code and pass the result as a simple variable.

---

## What is Mustache?

Mustache is a **logic-less** templating system. It intentionally has:
- ✅ **No if/else logic** - Use sections for conditionals
- ✅ **No loops with indexes** - Use implicit iterators
- ✅ **No filters/transformations** - Move formatting to code
- ✅ **No arithmetic** - Calculate before passing to template

**Philosophy:** Keep templates simple, move logic to code.

---

## Freeplay-Specific Behavior

⚠️ **Important differences from standard Mustache:**

1. **No character escaping** - Freeplay does NOT escape special characters (quotes, braces, etc.)
   - Standard Mustache: `{{name}}` escapes HTML
   - Freeplay: `{{name}}` outputs raw text
   - Implication: You can use quotes, braces, etc. in variables without issues

2. **Partials disabled** - `{{> partial}}` syntax is NOT supported
   - Cannot recursively include other prompts
   - All content must be in a single template

3. **Standard Mustache features supported:**
   - ✅ Variables: `{{name}}`
   - ✅ Dotted names: `{{user.email}}`
   - ✅ Sections: `{{#items}}...{{/items}}`
   - ✅ Inverted sections: `{{^items}}...{{/items}}`
   - ✅ Comments: `{{! this is a comment }}`
   - ✅ Implicit iterator: `{{.}}`

---

## Mustache Tag Reference

### 1. Variables

**Basic Variable:**
```mustache
Hello {{name}}!
```

**Dotted Names (Nested Objects):**
```mustache
Customer: {{customer.name}}
Email: {{customer.contact.email}}
```

**Implicit Iterator (Current Item):**
```mustache
{{#colors}}
  - {{.}}
{{/colors}}
```

**Missing Variables:**
- If variable doesn't exist: renders as empty string
- No errors thrown

---

### 2. Sections (Conditionals & Loops)

**Conditional Rendering:**
```mustache
{{#has_account}}
Welcome back!
{{/has_account}}
```

Renders the block if `has_account` is:
- `true`
- Non-empty string
- Non-zero number
- Non-empty array/list
- Non-null object

**List Iteration:**
```mustache
{{#items}}
  - {{name}}: ${{price}}
{{/items}}
```

For each item in `items`, renders the block with that item as context.

**Accessing Parent Context in Loops:**

⚠️ **Important:** Inside sections, you lose access to parent variables. Plan your data structure accordingly:

```mustache
{{! BAD - user_name not accessible inside #items }}
{{#items}}
  {{user_name}}'s item: {{name}}  {{! user_name won't work }}
{{/items}}

{{! GOOD - Include what you need in each item }}
{{#items}}
  {{owner_name}}'s item: {{name}}  {{! owner_name in each item }}
{{/items}}
```

**Python code to structure data correctly:**
```python
# Prepare data with nested info
variables = {
    "items": [
        {"owner_name": user_name, "name": "Widget", "price": 29.99},
        {"owner_name": user_name, "name": "Gadget", "price": 49.99}
    ]
}
```

---

### 3. Inverted Sections (If-Not)

**Render When False/Empty:**
```mustache
{{^items}}
  No items found.
{{/items}}
```

Renders the block if `items` is:
- `false`
- Empty string
- Empty array/list
- `null`/`undefined`

**If-Else Pattern:**
```mustache
{{#has_discount}}
Discount applied!
{{/has_discount}}
{{^has_discount}}
No discount available.
{{/has_discount}}
```

---

### 4. Comments

```mustache
{{! This is a comment and won't be rendered }}
{{! Comments can span
    multiple lines }}
```

---

## Common Conversions

### From Jinja2

| Jinja2 | Mustache | Notes |
|--------|----------|-------|
| `{{ name }}` | `{{name}}` | No spaces (convention) |
| `{% if active %}` | `{{#active}}` | Section for true |
| `{% else %}` | `{{/active}}{{^active}}` | Use inverted section |
| `{% for item in items %}` | `{{#items}}` | Iteration via section |
| `{{ item.name }}` | `{{name}}` | Direct access in loop |
| `{{ name\|upper }}` | Move to code | No filters in Mustache |
| `{% if x and y %}` | Move to code | No complex logic |

**Jinja Example:**
```jinja2
{% if user.is_premium %}
  Hello {{user.name|upper}}!
  {% for perk in user.perks %}
    - {{perk}}
  {% endfor %}
{% endif %}
```

**Mustache Equivalent:**
```mustache
{{#user_is_premium}}
  Hello {{user_name_upper}}!
  {{#perks}}
    - {{.}}
  {{/perks}}
{{/user_is_premium}}
```

**Python preprocessing:**
```python
variables = {
    "user_is_premium": user.is_premium,
    "user_name_upper": user.name.upper(),
    "perks": user.perks
}
```

---

### From Python f-strings

| f-string | Mustache | Notes |
|----------|----------|-------|
| `f"{name}"` | `{{name}}` | Direct replacement |
| `f"{user.email}"` | `{{user.email}}` | Dotted names work |
| `f"{name.upper()}"` | Move to code | No method calls |
| `f"{price:.2f}"` | Move to code | No formatting |

**f-string Example:**
```python
prompt = f"Hello {user.name}! You have {len(items)} items."
```

**Mustache Equivalent:**
```mustache
Hello {{user.name}}! You have {{item_count}} items.
```

**Python preprocessing:**
```python
variables = {
    "user": {"name": user.name},
    "item_count": len(items)
}
```

---

### From JavaScript Template Literals

| Template Literal | Mustache | Notes |
|-----------------|----------|-------|
| `` `${name}` `` | `{{name}}` | Direct replacement |
| `` `${user.email}` `` | `{{user.email}}` | Dotted names work |
| `` `${name.toUpperCase()}` `` | Move to code | No methods |

---

## What You CANNOT Do in Mustache

### ❌ Filters / Transformations

**Jinja:**
```jinja2
{{ name|upper }}
{{ description|truncate(100) }}
{{ price|round(2) }}
```

**Solution:** Pre-process in code:
```python
variables = {
    "name_upper": name.upper(),
    "description_short": description[:100] + "..." if len(description) > 100 else description,
    "price_rounded": round(price, 2)
}
```

```mustache
{{name_upper}}
{{description_short}}
{{price_rounded}}
```

---

### ❌ Complex Conditionals

**Jinja:**
```jinja2
{% if age >= 18 and has_license %}
  You can rent a car.
{% endif %}
```

**Solution:** Compute boolean in code:
```python
variables = {
    "can_rent_car": age >= 18 and has_license
}
```

```mustache
{{#can_rent_car}}
  You can rent a car.
{{/can_rent_car}}
```

---

### ❌ Loop Indexes

**Jinja:**
```jinja2
{% for i, item in enumerate(items) %}
  {{i+1}}. {{item}}
{% endfor %}
```

**Solution:** Add index in data:
```python
variables = {
    "items_indexed": [
        {"number": i+1, "name": item}
        for i, item in enumerate(items)
    ]
}
```

```mustache
{{#items_indexed}}
  {{number}}. {{name}}
{{/items_indexed}}
```

---

### ❌ Arithmetic

**Jinja:**
```jinja2
Total: {{ price * quantity }}
```

**Solution:** Calculate in code:
```python
variables = {
    "total": price * quantity
}
```

```mustache
Total: {{total}}
```

---

### ❌ Default Values

**Jinja:**
```jinja2
{{ name|default("Guest") }}
```

**Solution:** Set defaults in code:
```python
variables = {
    "display_name": name if name else "Guest"
}
```

```mustache
{{display_name}}
```

---

## Common Patterns for LLM Prompts

### Pattern 1: Conversation History

**Data structure:**
```python
variables = {
    "history": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ]
}
```

**Template:**
```mustache
{{#history}}
{{role}}: {{content}}
{{/history}}
```

**Output:**
```
user: Hello
assistant: Hi there!
user: How are you?
```

---

### Pattern 2: Conditional System Instructions

**Data structure:**
```python
variables = {
    "is_expert_mode": user.tier == "premium",
    "user_name": user.name,
    "special_instructions": "Use technical terminology and provide detailed explanations."
}
```

**Template:**
```mustache
You are a helpful assistant for {{user_name}}.

{{#is_expert_mode}}
{{special_instructions}}
{{/is_expert_mode}}
```

---

### Pattern 3: Optional Context

**Data structure:**
```python
variables = {
    "has_context": bool(context_data),
    "context": context_data if context_data else None
}
```

**Template:**
```mustache
{{#has_context}}
Relevant context:
{{context}}

Use this context to answer the question.
{{/has_context}}
{{^has_context}}
Answer based on your general knowledge.
{{/has_context}}
```

---

### Pattern 4: Lists of Items

**Data structure:**
```python
variables = {
    "has_products": len(products) > 0,
    "products": [
        {"name": "Widget", "price": "29.99", "in_stock": True},
        {"name": "Gadget", "price": "49.99", "in_stock": False}
    ]
}
```

**Template:**
```mustache
{{#has_products}}
Available products:
{{#products}}
- {{name}}: ${{price}} {{#in_stock}}(In Stock){{/in_stock}}{{^in_stock}}(Out of Stock){{/in_stock}}
{{/products}}
{{/has_products}}
{{^has_products}}
No products available.
{{/has_products}}
```

---

## Conversion Workflow

### Step 1: Identify Template Type

Determine the source format:
- Jinja2 (`.jinja`, `{% %}`, `{{ }}`)
- f-strings (Python `f""` or `.format()`)
- Template literals (JavaScript `` ` ` ``)
- Other (Go templates, ERB, etc.)

---

### Step 2: Extract Variables

List all variables used in the template:

```python
# Example template
original = """
Hello {{user.name}}!
{% if user.is_premium %}
  Your subscription expires: {{user.expiry|strftime('%Y-%m-%d')}}
{% endif %}
"""

# Variables identified:
# - user.name
# - user.is_premium (condition)
# - user.expiry (needs date formatting)
```

---

### Step 3: Identify Logic & Transformations

Mark areas that need preprocessing:
- ⚠️ Filters (`.upper()`, `|truncate`, etc.)
- ⚠️ Complex conditionals (`if x and y`)
- ⚠️ Loops with indexes
- ⚠️ Arithmetic operations
- ⚠️ Default values

---

### Step 4: Confirm Complex Logic with User

**⚠️ IMPORTANT:** Before converting complex templates, confirm the approach with the user:

```
I found complex logic in this template that needs to be moved to code:

1. Date formatting: {{user.expiry|strftime('%Y-%m-%d')}}
2. String transformation: {{name|upper}}
3. Conditional: {% if age >= 18 and has_license %}

I'll handle this by:
- Computing formatted_date in Python before passing to template
- Computing name_upper in Python
- Computing can_drive boolean in Python

The Mustache template will receive these pre-computed values.

Does this approach work for your use case, or would you prefer a different structure?
```

**Why this matters:**
- User may have specific requirements for how data is structured
- User may want to keep logic in one place
- User may need to understand the data contract between code and template

---

### Step 5: Pre-process Data Structure

Create the data structure that Mustache needs:

```python
# Compute all logic in code
from datetime import datetime

variables = {
    "user_name": user.name,
    "user_is_premium": user.is_premium,
    "expiry_formatted": user.expiry.strftime('%Y-%m-%d') if user.is_premium else None
}
```

---

### Step 6: Write Mustache Template

Convert to Mustache using pre-computed values:

```mustache
Hello {{user_name}}!
{{#user_is_premium}}
  Your subscription expires: {{expiry_formatted}}
{{/user_is_premium}}
```

---

### Step 7: Test with Sample Data

Always test with real data:

```python
import chevron  # Mustache renderer for Python

test_data = {
    "user_name": "Jane Doe",
    "user_is_premium": True,
    "expiry_formatted": "2024-12-31"
}

output = chevron.render(template, test_data)
print(output)

# Expected:
# Hello Jane Doe!
#   Your subscription expires: 2024-12-31
```

---

## Troubleshooting

### Issue: Variable not rendering

**Problem:**
```mustache
Hello {{user_name}}!
```
Output: `Hello !`

**Causes:**
1. Variable name mismatch (check spelling)
2. Variable not in data structure
3. Variable is `None`/`null`

**Solution:**
```python
# Check your data
print(variables)  # Is 'user_name' present?

# Ensure all variables are set
variables = {
    "user_name": user.name if user.name else "Guest"  # Fallback
}
```

---

### Issue: Section not rendering

**Problem:**
```mustache
{{#items}}
  - {{name}}
{{/items}}
```
Output: (nothing)

**Causes:**
1. `items` is empty array
2. `items` is `False`, `None`, `0`, or `""`
3. `items` doesn't exist in data

**Solution:**
```python
# Ensure items is non-empty
variables = {
    "items": items if items else []  # Empty array still won't render
}

# Or use inverted section for feedback
```

```mustache
{{#items}}
  - {{name}}
{{/items}}
{{^items}}
  No items found.
{{/items}}
```

---

### Issue: Can't access parent variable in loop

**Problem:**
```mustache
{{#items}}
  {{user_name}}'s item: {{name}}  {{! user_name not accessible }}
{{/items}}
```

**Solution:**
```python
# Include parent data in each item
variables = {
    "items": [
        {"user_name": user_name, "name": "Widget"},
        {"user_name": user_name, "name": "Gadget"}
    ]
}
```

Or restructure template:
```mustache
Items for {{user_name}}:
{{#items}}
  - {{name}}
{{/items}}
```

---

## Best Practices

### 1. Establish Data Contract

Before creating templates, define the data structure:

```python
# Document what the template expects
"""
Template: customer_greeting

Expected variables:
{
    "customer_name": str,           # Required
    "is_premium": bool,             # Required
    "account_balance": str,         # Optional, pre-formatted
    "recent_orders": [              # Optional list
        {"order_id": str, "total": str}
    ]
}
"""
```

### 2. Keep Templates Readable

**Bad:** Nested, complex structure
```mustache
{{#a}}{{#b}}{{#c}}{{d}}{{/c}}{{/b}}{{/a}}
```

**Good:** Clear hierarchy with whitespace
```mustache
{{#has_account}}
  {{#is_premium}}
    {{#has_orders}}
      Your recent order: {{order_id}}
    {{/has_orders}}
  {{/is_premium}}
{{/has_account}}
```

### 3. Pre-compute Everything

Move all logic to code:
```python
# GOOD - All logic in code
variables = {
    "greeting": f"Good {'morning' if hour < 12 else 'afternoon'}",
    "items_summary": f"{len(items)} item{'s' if len(items) != 1 else ''}",
    "formatted_price": f"${price:.2f}"
}
```

```mustache
{{greeting}}! You have {{items_summary}} for {{formatted_price}}.
```

### 4. Use Descriptive Variable Names

**Bad:**
```python
variables = {"d": data, "f": flag, "x": x_val}
```

**Good:**
```python
variables = {
    "customer_data": customer_info,
    "is_first_time_user": not has_previous_orders,
    "discount_percentage": calculate_discount(user)
}
```

### 5. Test Edge Cases

Always test with:
- Empty lists
- Missing optional values
- `None`/`null` values
- Empty strings
- Zero values

```python
test_cases = [
    {"items": []},                    # Empty list
    {"items": None},                  # Missing
    {"name": ""},                     # Empty string
    {"count": 0},                     # Zero
    {"optional_field": None}          # Null
]

for test in test_cases:
    output = chevron.render(template, test)
    assert output  # Verify it renders something valid
```

---

## Migration Checklist

When converting a template to Mustache for Freeplay:

- [ ] Identify source template format (Jinja, f-string, etc.)
- [ ] List all variables used
- [ ] Identify filters/transformations → move to code
- [ ] Identify complex conditionals → compute booleans in code
- [ ] Identify loops with indexes → add indexes to data
- [ ] **Confirm complex logic approach with user**
- [ ] Structure data for Mustache (nested objects, pre-computed values)
- [ ] Write Mustache template
- [ ] Test with sample data
- [ ] Test edge cases (empty, null, zero)
- [ ] Document expected data structure
- [ ] Verify no partials used (Freeplay limitation)

---

## Resources

- **Mustache Specification:** https://mustache.github.io/mustache.5.html
- **Freeplay Docs:** https://docs.freeplay.ai/core-concepts/prompt-management/advanced-prompt-templating-using-mustache
- **Python Mustache Renderer:** `pip install chevron`
- **JavaScript Mustache Renderer:** `npm install mustache`

---

## Summary

**Mustache Philosophy:** Logic-less templates with data preparation in code

**Freeplay Specifics:**
- No character escaping (quotes/braces work as-is)
- No partials (single template only)
- Standard Mustache features supported

**Conversion Process:**
1. Extract variables
2. Identify complex logic
3. **Confirm approach with user**
4. Move logic to code
5. Write Mustache template
6. Test thoroughly

**Key Rule:** If it requires logic, put it in code. If it requires formatting, put it in code. Templates should be pure structure and iteration.
