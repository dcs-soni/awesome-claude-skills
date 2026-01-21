# Postmortem Template & Guidelines

Blameless postmortems focus on systemic improvements, not individual blame.

---

## Template

```markdown
# Postmortem: [Incident Title]

**Date:** [YYYY-MM-DD]
**Severity:** [P1/P2/P3]
**Duration:** [X hours Y minutes]
**Authors:** [Names]
**Status:** [Draft/Review/Final]

## Summary

[1-2 sentences: What happened and what was the impact?]

## Impact

| Metric          | Value |
| --------------- | ----- |
| Duration        |       |
| Users Affected  |       |
| Revenue Impact  |       |
| Support Tickets |       |

## Timeline

| Time (UTC) | Event                 |
| ---------- | --------------------- |
| HH:MM      | First alert triggered |
| HH:MM      | On-call acknowledged  |
| HH:MM      | Initial diagnosis     |
| HH:MM      | Mitigation applied    |
| HH:MM      | Service restored      |

## Root Cause

[Detailed technical explanation of what caused the incident]

### 5 Whys Analysis

1. **Why** did the system fail? → [Answer]
2. **Why** did [Answer 1] happen? → [Answer]
3. **Why** did [Answer 2] happen? → [Answer]
4. **Why** did [Answer 3] happen? → [Answer]
5. **Why** did [Answer 4] happen? → [Root cause]

## Contributing Factors

- [ ] Recent deployment
- [ ] Configuration change
- [ ] External dependency failure
- [ ] Traffic spike
- [ ] Hardware failure
- [ ] Other: \_\_\_

## What Went Well

- [What helped us detect/resolve faster?]
- [What worked as designed?]

## What Went Wrong

- [What delayed detection?]
- [What made resolution harder?]

## Action Items

| Action            | Owner | Priority | Due Date   | Status |
| ----------------- | ----- | -------- | ---------- | ------ |
| [Specific action] | @name | P1/P2/P3 | YYYY-MM-DD | Open   |

## Lessons Learned

[Key takeaways for the team and organization]

## References

- [Link to incident channel]
- [Link to related PRs]
- [Link to monitoring dashboards]
```

---

## Guidelines

### Writing Effective Summaries

**Good:** "Database connection pool exhausted due to connection leak in UserService, causing 500 errors for 45 minutes affecting 12,000 users."

**Bad:** "Database was broken."

### 5 Whys Best Practices

- Keep asking until you reach a systemic issue
- Don't stop at human error (ask why the system allowed it)
- Multiple root causes are valid

### Action Items

Each action should be:

- **Specific** — "Add connection pool metrics" not "improve monitoring"
- **Assigned** — Has a clear owner
- **Prioritized** — P1 prevents recurrence, P2 improves detection
- **Time-bound** — Has a due date
- **Tracked** — Linked to ticket/issue

### Blameless Culture

- Focus on **systems**, not **people**
- Ask "How did the system allow this?" not "Who did this?"
- Celebrate learning, not blame
- Share postmortems widely
