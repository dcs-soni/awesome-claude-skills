---
name: finding-stale-todos
description:
  Find and analyze stale TODO, FIXME, HACK comments in codebases using
  git history. Use when user mentions stale TODOs, old comments, tech debt cleanup,
  forgotten TODOs, or code archaeology.
---

# Stale TODO Finder

Find forgotten TODO/FIXME/HACK comments and track their age using git blame.

## Quick Start

Copy this checklist:

```
Stale TODO Analysis:
- [ ] Step 1: Scan for TODO comments
- [ ] Step 2: Analyze staleness with git blame
- [ ] Step 3: Categorize by age
- [ ] Step 4: Generate actionable report
```

---

## Workflow

### Step 1: Scan for TODO Comments

Find all TODO-style comments in the codebase:

```bash
python scripts/find_todos.py <directory> --format json
```

**Patterns detected:**

- `TODO`, `FIXME`, `HACK`, `XXX`, `BUG`, `OPTIMIZE`
- Works across Python, JavaScript, TypeScript, Go, Java, C/C++, Ruby, Rust

### Step 2: Analyze Staleness

Correlate TODOs with git history:

```bash
python scripts/analyze_staleness.py <directory> --min-age 90
```

**Output includes:**

- Commit date when TODO was added
- Age in days
- Original author
- File and line number

### Step 3: Categorize by Age

TODOs are grouped into staleness buckets:

| Category   | Age         | Priority                |
| ---------- | ----------- | ----------------------- |
| 🔴 Ancient | >1 year     | High - likely forgotten |
| 🟠 Stale   | 6-12 months | Medium - needs review   |
| 🟡 Aging   | 3-6 months  | Low - monitor           |
| 🟢 Recent  | <3 months   | OK - still relevant     |

### Step 4: Generate Report

Create actionable markdown report:

```bash
python scripts/generate_report.py <directory> --output stale_todos.md
```

Report includes:

- Summary statistics
- TODOs sorted by age (oldest first)
- Grouped by category
- Author attribution

---

## Utility Scripts

| Script                 | Purpose                  |
| ---------------------- | ------------------------ |
| `find_todos.py`        | Find all TODO comments   |
| `analyze_staleness.py` | Git blame analysis       |
| `generate_report.py`   | Generate markdown report |

---

## Example

**User:** "Find forgotten TODOs in this project"

1. Run `find_todos.py .` → Finds 47 TODOs
2. Run `analyze_staleness.py .` → 12 are older than 1 year
3. Run `generate_report.py .` → Creates report with:
   - 12 ancient TODOs (>1 year)
   - 8 stale TODOs (6-12 months)
   - 27 recent TODOs (<6 months)

**Sample output:**

```markdown
## 🔴 Ancient TODOs (>1 year) - 12 found

| File         | Line | Age      | Author | Content                  |
| ------------ | ---- | -------- | ------ | ------------------------ |
| src/utils.py | 42   | 847 days | @alice | TODO: optimize this loop |
| lib/auth.js  | 156  | 623 days | @bob   | FIXME: handle edge case  |
```

---

## Configuration

Filter by patterns or paths:

```bash
# Only FIXME and BUG
python scripts/find_todos.py . --patterns FIXME,BUG

# Exclude vendor directories
python scripts/find_todos.py . --exclude "vendor/*,node_modules/*"

# Only show TODOs older than 6 months
python scripts/analyze_staleness.py . --min-age 180
```

---

## Related Skills

- **codebase-onboarding** — Understand codebase before cleanup
- **incident-response-helper** — Some TODOs may be related to incidents
