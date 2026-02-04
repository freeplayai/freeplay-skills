# Freeplay Skills

Skills for the [Freeplay Plugin](https://github.com/freeplayai/freeplay-plugin) for Claude Code.

## Installation

### Using OpenSkills

Install directly from GitHub using [OpenSkills](https://github.com/numman-ali/openskills):

```bash
npx openskills install git@github.com:freeplayai/freeplay-skills.git
```

### Manual Installation

Clone this repository into your skills directory:

**For Claude Code:**
```bash
git clone git@github.com:freeplayai/freeplay-skills.git ~/.config/claude-code/skills/freeplay-skills
```

**For Cursor (project-level):**
```bash
git clone git@github.com:freeplayai/freeplay-skills.git .cursor/skills/freeplay-skills
```

**For Cursor (global):**
```bash
git clone git@github.com:freeplayai/freeplay-skills.git ~/.cursor/skills/freeplay-skills
```

## Usage with Claude Code

These skills are auto-invoked by Claude based on context when using the Freeplay plugin. They are included as a git submodule in the main plugin repository.

## Usage with Cursor

These skills can also be used with [Cursor](https://cursor.com) through its [Agent Skills](https://cursor.com/docs/context/skills) system. When installed to `.claude/skills/` (via OpenSkills) or `.cursor/skills/` (via manual installation), Cursor automatically discovers and invokes them based on context.

Skills are separate from [Cursor Rules](https://cursor.com/docs/context/rules) (stored in `.cursor/rules/`) which provide persistent behavioral guidelines. Skills and rules work together - rules define how the AI should behave, while skills provide specialized capabilities that are auto-invoked when relevant.

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
