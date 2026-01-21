#!/usr/bin/env python3
"""
Postmortem Generator

Creates a postmortem document template pre-populated with incident data.
Usage: python create_postmortem.py --title "Incident Title" --severity P1 --output postmortem.md
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path


POSTMORTEM_TEMPLATE = '''# Postmortem: {title}

**Date:** {date}
**Severity:** {severity}
**Duration:** [TODO: Calculate from timeline]
**Authors:** [TODO: Add names]
**Status:** Draft

---

## Summary

[TODO: 1-2 sentences describing what happened and the impact]

---

## Impact

| Metric | Value |
|--------|-------|
| Duration | [TODO] |
| Users Affected | [TODO] |
| Revenue Impact | [TODO] |
| Support Tickets | [TODO] |
| SLA Breach | [TODO: Yes/No] |

---

## Timeline

All times in UTC.

| Time | Event |
|------|-------|
{timeline_placeholder}

---

## Detection

- **How was the issue detected?** [TODO: Alert, customer report, monitoring]
- **Time to detection:** [TODO: X minutes from incident start]
- **Detection gaps:** [TODO: What should have caught this sooner?]

---

## Root Cause

[TODO: Detailed technical explanation of what caused the incident]

### 5 Whys Analysis

1. **Why** did the system fail?
   → [TODO]

2. **Why** did [answer to #1] happen?
   → [TODO]

3. **Why** did [answer to #2] happen?
   → [TODO]

4. **Why** did [answer to #3] happen?
   → [TODO]

5. **Why** did [answer to #4] happen?
   → [TODO: This should be the root cause]

---

## Contributing Factors

Check all that apply:

- [ ] Recent deployment or release
- [ ] Configuration change
- [ ] External dependency failure
- [ ] Unexpected traffic spike
- [ ] Hardware/infrastructure failure
- [ ] Human error (process gap, not blame)
- [ ] Insufficient monitoring/alerting
- [ ] Missing runbook or documentation
- [ ] Other: ___

---

## Resolution

### What fixed the immediate issue?

[TODO: Describe the mitigation or fix]

### Resolution timeline

| Time | Action |
|------|--------|
| [TODO] | Issue identified |
| [TODO] | Mitigation applied |
| [TODO] | Service restored |
| [TODO] | Full resolution confirmed |

---

## What Went Well

- [TODO: What helped detect/resolve the issue faster?]
- [TODO: What worked as designed?]
- [TODO: Who/what was particularly helpful?]

---

## What Went Wrong

- [TODO: What delayed detection?]
- [TODO: What made resolution harder?]
- [TODO: What process gaps were exposed?]

---

## Action Items

| Priority | Action | Owner | Due Date | Ticket |
|----------|--------|-------|----------|--------|
| P1 | [TODO: Prevent recurrence] | @[name] | [date] | [link] |
| P2 | [TODO: Improve detection] | @[name] | [date] | [link] |
| P2 | [TODO: Improve recovery] | @[name] | [date] | [link] |
| P3 | [TODO: Documentation] | @[name] | [date] | [link] |

### Action Item Guidelines

- **P1**: Must complete to prevent recurrence
- **P2**: Important for detection or faster recovery
- **P3**: Nice to have, documentation, process improvements

---

## Lessons Learned

[TODO: Key takeaways for the team and organization]

1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

---

## References

- Incident channel: [TODO: Slack/Teams link]
- Related PRs: [TODO: Links]
- Monitoring dashboard: [TODO: Link]
- Related incidents: [TODO: Links to similar past incidents]

---

## Appendix

### Relevant Logs

```
[TODO: Include key log snippets]
```

### Metrics/Graphs

[TODO: Include relevant screenshots or graph links]

---

*This postmortem follows blameless culture principles. Focus on systemic improvements, not individual blame.*
'''


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate a postmortem document template'
    )
    parser.add_argument(
        '--title',
        required=True,
        help='Incident title'
    )
    parser.add_argument(
        '--severity',
        choices=['P1', 'P2', 'P3', 'SEV1', 'SEV2', 'SEV3'],
        default='P2',
        help='Incident severity (default: P2)'
    )
    parser.add_argument(
        '--output',
        default='postmortem.md',
        help='Output file path (default: postmortem.md)'
    )
    parser.add_argument(
        '--timeline-file',
        help='Path to timeline file to include'
    )
    return parser.parse_args()


def load_timeline(timeline_path):
    """Load timeline from file if provided."""
    if not timeline_path:
        return "| [TODO] | [TODO: First event] |\n| [TODO] | [TODO: Issue detected] |\n| [TODO] | [TODO: Mitigation applied] |\n| [TODO] | [TODO: Service restored] |"
    
    try:
        with open(timeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract just the events table if it exists
            lines = content.split('\n')
            timeline_lines = []
            in_table = False
            for line in lines:
                if line.startswith('| Time') or line.startswith('|---'):
                    in_table = True
                    continue
                if in_table and line.startswith('|'):
                    timeline_lines.append(line)
                elif in_table and not line.startswith('|'):
                    break
            if timeline_lines:
                return '\n'.join(timeline_lines)
    except Exception as e:
        print(f"Warning: Could not load timeline: {e}", file=sys.stderr)
    
    return "| [TODO] | [TODO: Add timeline events] |"


def main():
    args = parse_args()
    
    # Prepare template variables
    date = datetime.now().strftime('%Y-%m-%d')
    timeline = load_timeline(args.timeline_file)
    
    # Generate postmortem
    postmortem = POSTMORTEM_TEMPLATE.format(
        title=args.title,
        date=date,
        severity=args.severity,
        timeline_placeholder=timeline
    )
    
    # Write output
    output_path = Path(args.output)
    
    try:
        # Don't overwrite existing postmortem without confirmation
        if output_path.exists():
            print(f"Warning: {output_path} already exists.", file=sys.stderr)
            response = input("Overwrite? [y/N]: ").strip().lower()
            if response != 'y':
                print("Aborted.", file=sys.stderr)
                sys.exit(0)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(postmortem)
        
        print(f"Postmortem created: {output_path}")
        print(f"\nNext steps:")
        print(f"  1. Fill in the [TODO] sections")
        print(f"  2. Complete the 5 Whys analysis")
        print(f"  3. Assign owners to action items")
        print(f"  4. Schedule review meeting")
        
    except PermissionError:
        print(f"Error: Permission denied writing to {output_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
