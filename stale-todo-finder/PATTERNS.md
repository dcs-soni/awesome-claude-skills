# TODO Comment Patterns

Reference for TODO-style comment patterns across languages.

---

## Standard Patterns

| Pattern    | Common Usage                           |
| ---------- | -------------------------------------- |
| `TODO`     | Task to complete later                 |
| `FIXME`    | Known bug or issue to fix              |
| `HACK`     | Workaround, needs proper solution      |
| `XXX`      | Warning, dangerous or problematic code |
| `BUG`      | Known bug                              |
| `OPTIMIZE` | Performance improvement needed         |
| `REVIEW`   | Needs code review                      |
| `NOTE`     | Important context (not actionable)     |

---

## Language-Specific Patterns

### Python

```python
# TODO: implement caching
# FIXME: handle None case
# type: ignore  # Not a TODO
```

### JavaScript/TypeScript

```javascript
// TODO: add error handling
/* FIXME: race condition */
// @ts-ignore  # Not a TODO
```

### Go

```go
// TODO: add context parameter
// FIXME(username): memory leak
```

### Java

```java
// TODO: refactor this method
/* FIXME: null pointer risk */
```

### Rust

```rust
// TODO: implement Clone
// FIXME: unsafe block needs review
todo!()  // Macro - different from comment
```

---

## Priority Indicators

Some teams add priority to TODOs:

```
// TODO(P1): Critical, block release
// TODO(P2): Important, do soon
// TODO(P3): Nice to have
// TODO(@username): Assigned to person
```

---

## Anti-Patterns

Comments that look like TODOs but aren't:

```python
# This is not a TODO item
# Documentation about TODO feature
# Ignore these patterns
```

The scripts filter out:

- TODOs inside string literals
- TODOs in documentation about TODO features
- Test files checking for TODO detection
