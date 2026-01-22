# Empty Catch Patterns by Language

Reference for detecting empty/silent catch blocks across languages.

---

## JavaScript / TypeScript

### Empty Catch

```javascript
try { ... } catch (e) {}
try { ... } catch {}  // ES2019+ optional binding
```

### Comment-Only Catch

```javascript
catch (e) {
  // TODO: handle this
}
```

### Silent Return

```javascript
catch (e) {
  return null;
}
```

### Console-Only (still problematic)

```javascript
catch (e) {
  console.log(e);  // No actual handling
}
```

---

## Python

### Bare Except with Pass

```python
try:
    ...
except:
    pass
```

### Exception Swallowing

```python
except Exception:
    pass

except Exception as e:
    pass
```

### Silent Return

```python
except Exception:
    return None
```

---

## Java

### Empty Catch Block

```java
try {
    ...
} catch (Exception e) {
}
```

### Comment-Only

```java
catch (Exception e) {
    // Ignore
}
```

### Multiple Exceptions Swallowed

```java
catch (IOException | SQLException e) {
}
```

---

## Go

### Ignored Error (most common)

```go
result, _ := doSomething()  // Underscore ignores error
```

### Empty If Block

```go
if err != nil {
    // Nothing here
}
```

### Silent Return

```go
if err != nil {
    return
}
```

---

## C#

### Empty Catch

```csharp
try {
    ...
} catch (Exception) {
}
```

### Catch-All Swallowing

```csharp
catch {
    // Catches everything silently
}
```

---

## Rust

### Unwrap Without Context

```rust
let value = result.unwrap();  // Panics without info
```

### Silent Ok Match

```rust
match result {
    Ok(v) => v,
    Err(_) => default,  // Error ignored
}
```

---

## Risk Assessment Heuristics

| Context                      | Risk Level  |
| ---------------------------- | ----------- |
| In `async` function          | 🔴 Critical |
| In database/payment code     | 🔴 Critical |
| In API handler               | 🟠 High     |
| In utility function          | 🟡 Medium   |
| In test file                 | 🟢 Low      |
| Has `// intentional` comment | 🟢 Low      |
