# Incident Response Helper

A Claude skill for accelerating production incident response with log analysis, timeline generation, runbook guidance, and automated postmortem creation.

## Installation

Copy to your project or global Claude skills directory:

```bash
# Project-level
cp -r incident-response-helper /path/to/project/.claude/skills/

# Global (available in all projects)
cp -r incident-response-helper ~/.claude/skills/
```

## Usage

Ask Claude for help with incidents:

- "Help me respond to this production outage"
- "Analyze these error logs"
- "Create a postmortem for yesterday's incident"
- "My API is returning 500 errors, help me debug"

Claude will automatically use this skill and guide you through the 7-step workflow.

## Files

| File          | Purpose                               |
| ------------- | ------------------------------------- |
| SKILL.md      | Main instructions and 7-step workflow |
| RUNBOOKS.md   | Common incident resolution procedures |
| POSTMORTEM.md | Blameless postmortem template         |

## Utility Scripts

All scripts use Python standard library only (no pip install required).

### analyze_logs.py

Parse log files for error patterns:

```bash
python scripts/analyze_logs.py application.log
python scripts/analyze_logs.py application.log --format json
python scripts/analyze_logs.py application.log --tail 1000
```

### generate_timeline.py

Create incident timeline from logs:

```bash
python scripts/generate_timeline.py ./logs/
python scripts/generate_timeline.py ./logs/ --start "2024-01-15T10:00:00" --end "2024-01-15T12:00:00"
python scripts/generate_timeline.py app.log --output timeline.md
```

### create_postmortem.py

Generate postmortem template:

```bash
python scripts/create_postmortem.py --title "Database Connection Pool Exhaustion" --severity P1
python scripts/create_postmortem.py --title "API Latency Spike" --severity P2 --output postmortem.md
```

### check_health.py

Quick endpoint health check:

```bash
python scripts/check_health.py https://api.example.com/health
python scripts/check_health.py https://api.example.com --timeout 5
python scripts/check_health.py https://api.example.com -v  # verbose
```

## Workflow Overview

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

## Related Skills

- **codebase-onboarding** - Understand service architecture
- **api-docs-generator** - Document APIs for better debugging

## License

MIT
