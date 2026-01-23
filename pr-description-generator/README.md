# PR Description Generator

Generate high-quality Pull Request descriptions from git diffs and commits.

## Installation

```bash
cp -r pr-description-generator /path/to/project/.claude/skills/
```

## Usage

```bash
# Analyze changes
python scripts/analyze_changes.py --base main

# Generate PR description
python scripts/generate_description.py --base main

# Output to file
python scripts/generate_description.py --base main --output pr.md
```

## What It Generates

- **Summary** - Auto-generated from commits
- **Type of Change** - Feature, bugfix, refactor, docs
- **Changes Made** - Bullet list from commits
- **Files Changed** - Table with status
- **Testing Instructions** - Placeholder for your steps
- **Related Issues** - Extracted from commit messages (#123)
- **Checklist** - Standard review items

## Scripts

| Script                    | Purpose                          |
| ------------------------- | -------------------------------- |
| `analyze_changes.py`      | Parse git diff and commits       |
| `generate_description.py` | Generate PR description markdown |

## License

MIT
