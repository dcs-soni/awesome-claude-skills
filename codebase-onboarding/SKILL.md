---
name: codebase-onboarding
description: Help developers understand unfamiliar codebases quickly. Use when
  user mentions onboarding, understanding code, architecture overview, codebase
  tour, project structure, or asks "how does this work" about a project.
---

# Codebase Onboarding Skill

A comprehensive skill to help new developers understand large codebases quickly by generating architecture overviews, identifying entry points, tracing data flows, and creating navigable codebase maps.

## Quick Start

When a user asks to understand a codebase:

```
Onboarding Progress:
- [ ] Step 1: Analyze project structure
- [ ] Step 2: Identify entry points
- [ ] Step 3: Map key components
- [ ] Step 4: Trace data flows
- [ ] Step 5: Document patterns
- [ ] Step 6: Generate onboarding guide
```

## Workflow

### Step 1: Analyze Project Structure

Run the structure analyzer to understand the project layout:

```bash
python .claude/skills/codebase-onboarding/scripts/analyze_structure.py .
```

This will output:

- Project type (Node.js, Python, Go, etc.)
- Directory structure with descriptions
- Key configuration files found
- Detected frameworks and libraries

### Step 2: Identify Entry Points

Find where the application starts and its main interfaces:

```bash
python .claude/skills/codebase-onboarding/scripts/find_entry_points.py .
```

Entry points include:

- Main application files (index.js, main.py, main.go)
- API route handlers
- CLI entry points
- Event handlers and listeners

### Step 3: Map Key Components

Read and analyze the core components:

1. **Models/Types** - Data structures used throughout
2. **Services** - Business logic implementations
3. **Controllers/Handlers** - Request handling
4. **Utilities** - Shared helper functions
5. **Configuration** - App settings and constants

Use `Glob` and `Read` tools to explore these directories.

### Step 4: Trace Data Flows

For each major feature, trace how data moves:

```bash
python .claude/skills/codebase-onboarding/scripts/trace_data_flow.py . --feature "user authentication"
```

Document:

- Input sources (API, CLI, events)
- Processing steps
- Data transformations
- Output destinations (DB, API, files)

### Step 5: Document Patterns

Identify recurring patterns in the codebase. See [PATTERNS.md](PATTERNS.md) for common patterns to look for.

Key patterns to identify:

- Architectural patterns (MVC, Clean Architecture, etc.)
- Error handling approaches
- Logging conventions
- Testing strategies
- Naming conventions

### Step 6: Generate Onboarding Guide

Create a comprehensive onboarding document:

```bash
python .claude/skills/codebase-onboarding/scripts/generate_map.py . --output ONBOARDING.md
```

The guide should include:

- Architecture diagram (Mermaid)
- Component overview
- Data flow diagrams
- "Where to find X" quick reference
- Common tasks guide

## Output Format

Generate documentation in this structure:

```markdown
# [Project Name] - Developer Onboarding Guide

## Architecture Overview

[Mermaid diagram showing major components]

## Project Structure

[Directory tree with descriptions]

## Key Components

[Table of important files and their purposes]

## Data Flows

[Diagrams showing how data moves through the system]

## Common Tasks

- How to add a new API endpoint
- How to add a new feature
- How to run tests
- How to deploy

## Patterns & Conventions

[Coding standards used in this project]
```

## Examples

### Example 1: Node.js Express API

**User:** "Help me understand this codebase"

**Steps:**

1. Run `analyze_structure.py` → Detects Node.js/Express
2. Run `find_entry_points.py` → Finds `src/index.js`, route files
3. Read package.json, tsconfig.json for dependencies
4. Map: routes/ → controllers/ → services/ → models/
5. Generate architecture diagram
6. Create ONBOARDING.md with quick reference

### Example 2: Python Django Project

**User:** "I'm new to this project, give me an overview"

**Steps:**

1. Detect Django from `manage.py`, `settings.py`
2. Find apps in `INSTALLED_APPS`
3. Map: urls.py → views.py → models.py
4. Trace request flow through middleware
5. Document ORM patterns and migrations
6. Generate Django-specific onboarding guide

## Tips for Success

1. **Start high-level** - Don't dive into implementation details initially
2. **Follow imports** - Trace import chains to understand dependencies
3. **Read tests** - Tests often reveal intended behavior
4. **Check docs/** - Existing documentation is valuable context
5. **Look for README** - Project README often explains structure

## Related Skills

- For API documentation: see API docs skill
- For dependency analysis: see dependency audit skill
- For code quality: see code review skill
