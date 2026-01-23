---
name: finding-orphan-files
description:
  Identify source files that are never imported or referenced (orphan files) to help clean up technical debt and reduce build size.
  Use when user mentions dead code, unused files, cleaning up codebase, or dependency audit.
run-in-subagent: true
allowed-tools:
  - View
  - Bash
  - Read
  - Grep
---

# Orphan File Finder

Detects "orphan" source files—those with no inbound references—to surface potentially unused code.

## Why This Matters

- **Reduce Technical Debt**: Unused files rot over time and mislead developers.
- **Shrink Bundle Size**: Dead code might still be bundled or deployed.
- **Security**: Forgotten endpoints or scripts can be attack vectors.

## Quick Start

```
Orphan File Cleanup:
- [ ] Step 1: Scan codebase for orphans
- [ ] Step 2: Review and whitelist entry points
- [ ] Step 3: Archive or delete verified dead files
```

---

## Workflow

### Step 1: Scan for Orphans

Analyze the dependency graph to find files with 0 inbound imports:

```bash
python scripts/find_orphans.py <directory>
```

**What it does:**

1. Indexes all source files (.js, .ts, .py).
2. Parses imports to build a directed graph.
3. Reports files that no other file imports.

### Step 2: Review & Verify

The script output splits findings into:

- **Potential Orphans**: Files with no imports.
- **Likely Entry Points**: Files matching patterns like `index.js`, `main.py`, `server.ts`.

Example output:

```
Found 12 potential orphan files.

Likely Entry Points (whitelist these?):
- src/index.ts
- src/cli.ts

Potential True Orphans:
- src/legacy/OldHelper.ts
- src/utils/Deprecated.js
```

### Step 3: Archive or Delete

Once verified:

1. Move to a `_archive/` folder if unsure.
2. Or delete: `rm src/legacy/OldHelper.ts`

---

## Configuration

**Auto-Whitelisted Patterns:**

- `index.js/ts/jsx/tsx`
- `main.py/js/ts`
- `server.js/ts`
- `app.js/ts`
- `cli.js/py`
- `setup.py`
- `manage.py` (Django)
- `vite.config.*`, `webpack.config.*`

**Supported Import Styles:**

- **JS/TS**: `import ... from`, `require(...)`, `export ... from`
- **Python**: `import module`, `from module import ...`

---

## Utility Scripts

| Script            | Purpose                                                   |
| ----------------- | --------------------------------------------------------- |
| `find_orphans.py` | Builds dependency graph and identifies disconnected nodes |

---

## Related Skills

- **stale-todo-finder** — Clean up old comments while cleaning up old files.
- **codebase-onboarding** — Understanding the graph helps with onboarding.
