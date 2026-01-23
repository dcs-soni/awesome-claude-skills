---
name: generating-pr-descriptions
description:
  Generate high-quality Pull Request descriptions from git diffs and commit history.
  Use when user mentions PR description, pull request, code review, or asks to write/generate a PR.
---

# PR Description Generator

Generate structured, comprehensive Pull Request descriptions from your git changes.

## Why This Matters

Good PR descriptions:

- **Speed up reviews** - Reviewers understand context instantly
- **Reduce bugs** - Testing instructions catch issues early
- **Create documentation** - Git history becomes useful

## Quick Start

```
PR Description Workflow:
- [ ] Step 1: Analyze changes (diff + commits)
- [ ] Step 2: Detect PR type
- [ ] Step 3: Generate description
- [ ] Step 4: Copy to PR
```

---

## Workflow

### Step 1: Analyze Changes

Run the analysis script to understand what changed:

```bash
python scripts/analyze_changes.py --base main
```

**What it extracts:**

- Files added, modified, deleted
- Commit messages and authors
- Issue references (#123, fixes #456)
- Change statistics (lines added/removed)

### Step 2: Detect PR Type

The script auto-detects the type based on:

| Type         | Detection                            |
| ------------ | ------------------------------------ |
| **Feature**  | New files, `feat:` commits           |
| **Bugfix**   | `fix:`, `bug:` commits, issue refs   |
| **Refactor** | `refactor:` commits, same file count |
| **Docs**     | Only `.md` files, `docs:` commits    |
| **Chore**    | Config files, `chore:` commits       |

### Step 3: Generate Description

Generate a complete PR description:

```bash
python scripts/generate_description.py --base main --output pr.md
```

**Output includes:**

- Summary (auto-generated from commits)
- Type of change checkboxes
- Detailed changes list
- Testing instructions
- Related issues
- Review checklist

### Step 4: Copy to PR

Copy the generated markdown to your PR:

- GitHub: Paste into description field
- GitLab: Paste into MR description
- Bitbucket: Paste into PR description

---

## Utility Scripts

| Script                    | Purpose                          |
| ------------------------- | -------------------------------- |
| `analyze_changes.py`      | Parse git diff and commits       |
| `generate_description.py` | Generate PR description markdown |

---

## Configuration

**Customize base branch:**

```bash
python scripts/generate_description.py --base develop
python scripts/generate_description.py --base origin/main
```

**Output to file:**

```bash
python scripts/generate_description.py --output pr_description.md
```

---

## Example

**User:** "Generate a PR description for my changes"

**Generated Output:**

```markdown
## Summary

Adds user authentication with JWT tokens and password hashing.

## Type of Change

- [x] ✨ New feature
- [ ] 🐛 Bug fix
- [ ] ♻️ Refactoring
- [ ] 📝 Documentation

## Changes Made

- Added `POST /auth/login` endpoint with JWT token generation
- Added `POST /auth/register` endpoint with validation
- Added bcrypt password hashing
- Added JWT middleware for protected routes

## Files Changed

| Status   | File                    |
| -------- | ----------------------- |
| Added    | src/auth/login.ts       |
| Added    | src/auth/register.ts    |
| Modified | src/middleware/index.ts |

## Testing Instructions

1. Register: `curl -X POST /auth/register -d '{"email":"test@test.com","password":"secret"}'`
2. Login: `curl -X POST /auth/login -d '{"email":"test@test.com","password":"secret"}'`
3. Access protected route with `Authorization: Bearer <token>`

## Related Issues

Closes #42

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## Templates

See [TEMPLATES.md](TEMPLATES.md) for PR templates by change type.

---

## Related Skills

- **codebase-onboarding** — Understand the codebase before reviewing
- **stale-todo-finder** — Ensure no stale TODOs in changed files
