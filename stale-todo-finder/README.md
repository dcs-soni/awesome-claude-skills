# Stale TODO Finder

A Claude skill for finding and analyzing stale TODO/FIXME/HACK comments in codebases using git history.

## Installation

```bash
# Project-level
cp -r stale-todo-finder /path/to/project/.claude/skills/

# Global
cp -r stale-todo-finder ~/.claude/skills/
```

## Usage

Ask Claude for help with stale TODOs:

- "Find forgotten TODOs in this project"
- "Show me old FIXME comments"
- "Analyze tech debt from TODO comments"

## Scripts

### find_todos.py

Find all TODO comments:

```bash
python scripts/find_todos.py .
python scripts/find_todos.py . --format json
python scripts/find_todos.py . --patterns FIXME,BUG
```

### analyze_staleness.py

Analyze age using git blame:

```bash
python scripts/analyze_staleness.py .
python scripts/analyze_staleness.py . --min-age 180
```

### generate_report.py

Generate markdown report:

```bash
python scripts/generate_report.py . --output stale_todos.md
```

## Staleness Categories

| Category | Age         | Emoji |
| -------- | ----------- | ----- |
| Ancient  | >1 year     | 🔴    |
| Stale    | 6-12 months | 🟠    |
| Aging    | 3-6 months  | 🟡    |
| Recent   | <3 months   | 🟢    |

## License

MIT
