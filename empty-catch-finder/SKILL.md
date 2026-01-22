---
name: finding-empty-catches
description:
  Find empty catch blocks and silent error handlers that swallow exceptions.
  Use when user mentions silent failures, error swallowing, empty catch, ignored exceptions,
  or debugging mysterious production issues.
---

# Empty Catch Block Finder

Detect silent error handlers that cause mysterious production failures.

## Why This Matters

Empty catch blocks are **silent killers**:

```javascript
try {
  await saveOrder(order);
} catch (e) {
  // Silent failure - order lost, no evidence
}
```

This skill finds them before they cause production incidents.

## Quick Start

```
Empty Catch Analysis:
- [ ] Step 1: Scan for empty catch blocks
- [ ] Step 2: Assess risk level
- [ ] Step 3: Generate fix suggestions
```

---

## Workflow

### Step 1: Scan for Empty Catches

Find all empty/silent catch blocks:

```bash
python scripts/find_empty_catches.py <directory>
```

**Detects:**

- `catch (e) {}` - completely empty
- `catch (e) { /* comment */ }` - only comments
- `except: pass` - Python silent pass
- `if err != nil { }` - Go ignored errors
- `catch { return; }` - silent returns

### Step 2: Assess Risk Level

Each catch is categorized by risk:

| Risk        | Pattern                            | Why Dangerous            |
| ----------- | ---------------------------------- | ------------------------ |
| 🔴 Critical | Empty catch in async/database code | Data loss, corruption    |
| 🟠 High     | Empty catch in API handlers        | Silent failures to users |
| 🟡 Medium   | Empty catch in utilities           | Hidden bugs              |
| 🟢 Low      | Empty catch in tests/scripts       | Usually intentional      |

### Step 3: Generate Fix Suggestions

Get suggested fixes:

```bash
python scripts/generate_fixes.py <directory> --output fixes.md
```

**Fix patterns:**

```javascript
// ❌ Before: Silent failure
catch (e) {}

// ✅ After: Logged + handled
catch (e) {
  logger.error('Order save failed', { error: e, orderId: order.id });
  throw new OrderSaveError('Failed to save order', { cause: e });
}
```

---

## Utility Scripts

| Script                  | Purpose                       |
| ----------------------- | ----------------------------- |
| `find_empty_catches.py` | Find empty catch blocks       |
| `generate_fixes.py`     | Suggest proper error handling |

---

## Language Support

| Language              | Patterns Detected                       |
| --------------------- | --------------------------------------- |
| JavaScript/TypeScript | `catch (e) {}`, `catch {}`              |
| Python                | `except: pass`, `except Exception: ...` |
| Java                  | `catch (Exception e) {}`                |
| Go                    | `if err != nil { }` (empty body)        |
| C#                    | `catch (Exception) {}`                  |

See [PATTERNS.md](PATTERNS.md) for full pattern reference.

---

## Example

**User:** "Find silent error handlers in my codebase"

**Output:**

```
Found 8 empty catch blocks

🔴 CRITICAL (2)
  src/services/payment.ts:45
    catch (e) {} // In async payment processing!

  src/db/users.ts:112
    catch (e) { return null; } // Hides DB errors

🟠 HIGH (3)
  src/api/orders.ts:78
    catch (error) { /* TODO: handle */ }

  ...
```

---

## Integration with Linting

After fixing, prevent new empty catches:

**ESLint:**

```json
{ "rules": { "no-empty": ["error", { "allowEmptyCatch": false }] } }
```

**Python (Ruff):**

```toml
[tool.ruff]
select = ["E722"]  # bare-except
```

---

## Related Skills

- **incident-response-helper** — Debug issues caused by silent failures
- **stale-todo-finder** — Find `// TODO: handle error` comments
