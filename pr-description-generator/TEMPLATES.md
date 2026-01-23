# PR Description Templates

Templates for different types of Pull Requests.

---

## Feature PR

```markdown
## Summary

[Brief description of the new feature]

## Type of Change

- [x] ✨ New feature
- [ ] 🐛 Bug fix
- [ ] ♻️ Refactoring
- [ ] 📝 Documentation

## Motivation

Why is this feature needed? Link to issue or explain the use case.

## Changes Made

- [List of specific changes]
- [Another change]

## Screenshots/Demos

[If UI changes, add screenshots]

## Testing Instructions

1. [Step to test]
2. [Another step]

## Related Issues

Closes #[issue number]

## Checklist

- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or migration guide provided)
- [ ] Accessibility considered (if UI)
```

---

## Bugfix PR

```markdown
## Summary

Fixes [brief description of the bug]

## Type of Change

- [ ] ✨ New feature
- [x] 🐛 Bug fix
- [ ] ♻️ Refactoring
- [ ] 📝 Documentation

## Bug Description

**What was happening:**
[Describe the incorrect behavior]

**Root Cause:**
[What caused the bug]

## Solution

[How you fixed it]

## Testing

**Before fix:**
[How to reproduce the bug]

**After fix:**
[How to verify it's fixed]

## Related Issues

Fixes #[issue number]

## Checklist

- [ ] Regression test added
- [ ] Root cause addressed (not just symptoms)
- [ ] Similar code checked for same issue
```

---

## Refactor PR

```markdown
## Summary

Refactors [component/module] to [improve X]

## Type of Change

- [ ] ✨ New feature
- [ ] 🐛 Bug fix
- [x] ♻️ Refactoring
- [ ] 📝 Documentation

## Motivation

Why this refactor? (Performance, readability, maintainability)

## Changes Made

- [Structural change 1]
- [Structural change 2]

## Behavior Changes

**None** - This is a pure refactor with no behavior changes.

## Testing

All existing tests pass. No new tests needed (behavior unchanged).

## Checklist

- [ ] All tests pass
- [ ] No behavior changes
- [ ] Performance benchmarks (if applicable)
```

---

## Documentation PR

```markdown
## Summary

Updates documentation for [area]

## Type of Change

- [ ] ✨ New feature
- [ ] 🐛 Bug fix
- [ ] ♻️ Refactoring
- [x] 📝 Documentation

## Changes Made

- [Doc change 1]
- [Doc change 2]

## Checklist

- [ ] Spelling/grammar checked
- [ ] Links verified
- [ ] Code examples tested
```

---

## Breaking Change PR

````markdown
## ⚠️ Breaking Change

## Summary

[Description of breaking change]

## Type of Change

- [x] 💥 Breaking change

## What Breaks

- [API that changes]
- [Behavior that changes]

## Migration Guide

### Before

```code
// Old way
```
````

### After

```code
// New way
```

## Why Breaking?

[Justification for the breaking change]

## Checklist

- [ ] Migration guide included
- [ ] CHANGELOG updated
- [ ] Version bump appropriate (major)

```

---

## Conventional Commit Prefixes

| Prefix | Description |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `style:` | Formatting, no code change |
| `refactor:` | Code change, no new feature or fix |
| `perf:` | Performance improvement |
| `test:` | Adding tests |
| `chore:` | Build, CI, tooling |
| `revert:` | Reverting a commit |
```
