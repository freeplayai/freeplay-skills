# Freeplay Skills

Skills for the [Freeplay Plugin](https://github.com/freeplayai/freeplay-plugin) that teach Claude Code and Cursor to analyze logs, iterate on prompts and agents, and run experiments in [Freeplay](https://freeplay.ai), the ops platform for AI engineering teams.

## ⚠️ EXPERIMENTAL

**These skills are experimental and will change.** Use at your own risk.

When used with the Freeplay MCP server, these skills instruct agents that have access to your Freeplay API key. A compromised agent could extract the key and perform actions against your Freeplay account outside the scope of these skills. Only use with agents you fully trust.

---

## Installation

### Using OpenSkills

Install directly from GitHub using [OpenSkills](https://github.com/numman-ali/openskills):

```bash
npx openskills install https://github.com/freeplayai/freeplay-skills.git
```

### Manual Installation

Clone this repository into your skills directory:

**For Claude Code:**
```bash
git clone https://github.com/freeplayai/freeplay-skills.git ~/.config/claude-code/skills/freeplay-skills
```

**For Cursor (project-level):**
```bash
git clone https://github.com/freeplayai/freeplay-skills.git .cursor/skills/freeplay-skills
```

**For Cursor (global):**
```bash
git clone https://github.com/freeplayai/freeplay-skills.git ~/.cursor/skills/freeplay-skills
```

## Required Environment Variables

The following environment variables must be set:

| Variable | Description |
|----------|-------------|
| `FREEPLAY_API_KEY` | Your Freeplay API key (required) |
| `FREEPLAY_API_BASE` | Freeplay API base URL (required) |

**Security Note:** API keys are handled securely and should never be logged or printed. The `SecretString` wrapper ensures keys are displayed as `[REDACTED]` if accidentally printed.

## Project ID

Project ID can come from:
- User specification
- MCP `list_projects()` tool to discover available projects
- `--project-id` CLI arg (for scripts)

## Usage with Claude Code

These skills are auto-invoked by Claude based on context when using the Freeplay plugin. They capture workflows and best practices for working with Freeplay's connected data flywheel: observability, prompt management, datasets, evaluations, and testing. Skills are included as a git submodule in the main plugin repository.

## Usage with Cursor

These skills can also be used with [Cursor](https://cursor.com) through its [Agent Skills](https://cursor.com/docs/context/skills) system. When installed to `.claude/skills/` (via OpenSkills) or `.cursor/skills/` (via manual installation), Cursor automatically discovers and invokes them based on context.

Skills are separate from [Cursor Rules](https://cursor.com/docs/context/rules) (stored in `.cursor/rules/`) which provide persistent behavioral guidelines. Skills and rules work together — rules define how the AI should behave, while skills provide specialized workflows that are auto-invoked when relevant.

## Shared Scripts

The `scripts/` directory contains shared utilities used across multiple skills:

- **`api.py`** - A small subset of API calls that can be used. 
- **`secrets.py`** - Secure handling of API keys with `SecretString` wrapper

Skills should symlink to these shared modules rather than duplicating code. See [`scripts/README.md`](scripts/README.md) for details.

## Adding a New Skill

Create a directory with a `SKILL.md` file:

```
skills/
└── my-skill/
    └── SKILL.md
```

The `SKILL.md` file should include frontmatter:

```markdown
---
name: my-skill
description: When Claude should auto-invoke this skill
---

Instructions for the skill.
```

## Support

- **Docs**: https://docs.freeplay.ai
- **Issues**: https://github.com/freeplayai/freeplay-skills/issues
- **Security**: security@freeplay.ai
