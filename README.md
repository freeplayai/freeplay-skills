# Freeplay Skills

Skills for the [Freeplay Plugin](https://github.com/freeplayai/freeplay-plugin) for Claude Code.

## Skills

| Skill | Description |
|-------|-------------|
| `deployed-prompts` | Look up deployed prompt versions in Freeplay |
| `freeplay-api` | Reference for writing code that interacts with the Freeplay API |
| `test-run-analysis` | Analyze Freeplay test runs for insights and metrics |

## Usage

These skills are auto-invoked by Claude based on context when using the Freeplay plugin. They are included as a git submodule in the main plugin repository.

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
