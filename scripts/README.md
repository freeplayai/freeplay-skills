# Shared Scripts

Shared utility modules used across multiple skills.

## Available Modules

### `secrets.py`

Utilities for secure handling of API keys and secrets. Prevents accidental exposure of sensitive values in logs, error messages, and console output.

**Classes:**

- `SecretString` - A string wrapper that shows `[REDACTED]` when printed. Use `.get()` to access the actual value.

**Functions:**

- `redact_secrets(text)` - Remove potential secrets from text before logging
- `safe_error_message(response_text)` - Create safe error messages from API responses

**Usage:**

```python
from secrets import SecretString, safe_error_message

# Wrap API keys
api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))

print(api_key)  # Output: [REDACTED]

# Access actual value when needed
headers = {"Authorization": f"Bearer {api_key.get()}"}

# Safe error handling
except requests.RequestException as e:
    print(f"Error: {safe_error_message(response.text)}")
```

## Using Shared Scripts in Skills

Skills should symlink to shared scripts rather than duplicating them:

```bash
# From your skill's scripts directory
ln -s ../../scripts/secrets.py secrets.py
```

This ensures:
- Single source of truth for shared code
- Security fixes automatically apply to all skills
- Consistent behavior across skills
