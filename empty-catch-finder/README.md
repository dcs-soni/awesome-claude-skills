# Empty Catch Block Finder

Find and fix silent error handlers that cause mysterious production failures.

## Installation

```bash
cp -r empty-catch-finder /path/to/project/.claude/skills/
```

## Usage

```bash
# Find empty catches
python scripts/find_empty_catches.py .

# Generate fix suggestions
python scripts/generate_fixes.py . --output fixes.md
```

## What It Detects

| Language | Pattern                                 |
| -------- | --------------------------------------- |
| JS/TS    | `catch (e) {}`, silent returns          |
| Python   | `except: pass`, `except Exception: ...` |
| Java     | `catch (Exception e) {}`                |
| Go       | `_, err :=`, empty `if err != nil`      |
| C#       | `catch {}`, `catch (Exception) {}`      |

## Risk Levels

| Level       | Meaning                        |
| ----------- | ------------------------------ |
| 🔴 Critical | In async/database/payment code |
| 🟠 High     | In API handlers                |
| 🟡 Medium   | General code                   |
| 🟢 Low      | Tests, intentional             |

## License

MIT
