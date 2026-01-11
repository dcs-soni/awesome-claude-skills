# Codebase Onboarding Skill

A Claude Code Skill that helps new developers understand large codebases quickly by generating architecture overviews, identifying entry points, tracing data flows, and creating navigable codebase maps.

## Installation

### Option 1: Copy to your project

Copy the `.claude/skills/codebase-onboarding/` directory to your project:

```bash
cp -r codebase-onboarding /path/to/your/project/.claude/skills/
```

### Option 2: Copy to global Claude skills

```bash
cp -r codebase-onboarding ~/.claude/skills/
```

## Usage

Once installed, Claude Code will automatically use this skill when you ask about understanding a codebase:

### Example prompts:

- "Help me understand this codebase"
- "Give me an architecture overview"
- "I'm new to this project, where do I start?"
- "Create an onboarding guide for this repo"
- "Trace the data flow for user authentication"
- "Find the entry points in this project"

## Included Scripts

| Script                 | Purpose                               | Usage                                                     |
| ---------------------- | ------------------------------------- | --------------------------------------------------------- |
| `analyze_structure.py` | Analyze project structure and type    | `python scripts/analyze_structure.py .`                   |
| `find_entry_points.py` | Find main files, routes, CLI commands | `python scripts/find_entry_points.py .`                   |
| `trace_data_flow.py`   | Trace data through the codebase       | `python scripts/trace_data_flow.py . --feature "auth"`    |
| `generate_map.py`      | Generate onboarding documentation     | `python scripts/generate_map.py . --output ONBOARDING.md` |

## Supported Project Types

- **Node.js / TypeScript** (Express, Fastify, Next.js, NestJS, React, Vue)
- **Python** (Django, Flask, FastAPI)
- **Go** (Gin, Echo)
- **Rust** (Cargo projects)

## Reference Files

- `PATTERNS.md` - Common architectural and coding patterns
- `ARCHITECTURE.md` - Framework detection and directory structure reference

## Example Output

When you ask Claude to understand a codebase, it will:

1. **Analyze Structure** - Identify project type, frameworks, key files
2. **Find Entry Points** - Locate main files, API routes, CLI commands
3. **Map Components** - Document key services, models, utilities
4. **Generate Documentation** - Create a comprehensive onboarding guide

### Sample Generated Guide

```markdown
# my-project - Developer Onboarding Guide

## Architecture Overview

[Mermaid diagram]

## Project Structure

src/
components/ # UI components
services/ # Business logic
routes/ # API routes
...

## Key Components

| File         | Description |
| ------------ | ----------- |
| src/index.ts | Entry point |

| ...
```

## Requirements

- Python 3.7+ (for utility scripts)
- Claude Code installed and configured

## Contributing

Feel free to extend this skill with:

- Support for additional frameworks
- More analysis patterns
- Custom documentation templates

## License

MIT
