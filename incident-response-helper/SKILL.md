---
name: responding-to-incidents
description:
  Assist with production incident response, log analysis, timeline creation,
  and postmortem generation. Use when user mentions incident, outage, production issue,
  debugging production, service down, error spikes, or postmortem.
---

# Incident Response Helper

Accelerate incident response with structured workflows, log analysis scripts, and automated postmortem generation.

## Quick Start

When responding to an incident, copy this checklist:

```
Incident Response Progress:
- [ ] Step 1: Initial Assessment
- [ ] Step 2: Collect & Analyze Logs
- [ ] Step 3: Build Timeline
- [ ] Step 4: Assess Impact
- [ ] Step 5: Root Cause Analysis
- [ ] Step 6: Resolve & Verify
- [ ] Step 7: Generate Postmortem
```

---

## Workflow

### Step 1: Initial Assessment

Gather information quickly:

1. **What's broken?** — Identify affected services/endpoints
2. **Severity?** — P1 (total outage), P2 (major degradation), P3 (partial impact)
3. **When did it start?** — Approximate start time
4. **Who's affected?** — Users, regions, features

Run quick health check if URL known:

```bash
python scripts/check_health.py <url> --timeout 10
```

### Step 2: Collect & Analyze Logs

Gather logs from affected services and analyze:

```bash
python scripts/analyze_logs.py <log_file> --format json
```

**Output includes:**

- Error patterns and frequency
- Exception stack traces
- Latency anomalies
- HTTP status code distribution

For multiple log files, run against each and compare patterns.

### Step 3: Build Timeline

Generate chronological incident timeline:

```bash
python scripts/generate_timeline.py <log_dir> --start "YYYY-MM-DDTHH:MM:SS" --end "YYYY-MM-DDTHH:MM:SS"
```

Key events to identify:

- First error occurrence
- Deployment or config changes
- Traffic patterns
- External dependencies failures

### Step 4: Assess Impact

Quantify the damage:

| Metric         | How to measure              |
| -------------- | --------------------------- |
| Duration       | End time - Start time       |
| Users affected | Error logs, support tickets |
| Revenue impact | Failed transactions         |
| Data loss      | Check persistence layer     |

### Step 5: Root Cause Analysis

Apply systematic analysis:

1. **What changed?** — Deployments, configs, dependencies
2. **5 Whys** — Keep asking "why" until root cause found
3. **Contributing factors** — List all factors, not just primary cause

For common issues, see [RUNBOOKS.md](RUNBOOKS.md).

### Step 6: Resolve & Verify

1. **Implement fix** — Code change, rollback, or config update
2. **Verify resolution** — Run health checks, monitor metrics
3. **Communicate** — Update stakeholders

Verification:

```bash
python scripts/check_health.py <url> --timeout 10
# Verify logs show no new errors
python scripts/analyze_logs.py <new_logs> --format text
```

### Step 7: Generate Postmortem

Create blameless postmortem document:

```bash
python scripts/create_postmortem.py --title "Incident Title" --severity P1 --output postmortem.md
```

See [POSTMORTEM.md](POSTMORTEM.md) for template and guidelines.

---

## Utility Scripts

| Script                 | Purpose                         |
| ---------------------- | ------------------------------- |
| `analyze_logs.py`      | Parse logs, find error patterns |
| `generate_timeline.py` | Create timeline from logs       |
| `create_postmortem.py` | Generate postmortem template    |
| `check_health.py`      | Quick endpoint health check     |

---

## Examples

### Example 1: Database Connection Exhaustion

**User:** "Our API is returning 500s, help me investigate"

1. Run `check_health.py` → Confirms 500 errors
2. Run `analyze_logs.py` on API logs → Finds "connection pool exhausted"
3. Run `generate_timeline.py` → Shows spike after traffic increase
4. Check [RUNBOOKS.md](RUNBOOKS.md) → Database section has resolution
5. Fix: Increase pool size, verify with health check
6. Generate postmortem

### Example 2: Deployment Caused Regression

**User:** "Users reporting slow responses after deploy"

1. Initial assessment: P2, latency issue
2. Analyze logs → High latency in specific endpoint
3. Timeline → Correlates with deployment time
4. Root cause → N+1 query introduced in new code
5. Resolution → Rollback deployment
6. Create postmortem with action items

---

## Related Skills

- **codebase-onboarding** — Understand service architecture first
- **api-docs-generator** — Document API for better debugging
