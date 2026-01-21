#!/usr/bin/env python3
"""
Timeline Generator

Creates an incident timeline from log files by extracting and ordering events.
Usage: python generate_timeline.py <log_dir> --start "YYYY-MM-DDTHH:MM:SS" --end "YYYY-MM-DDTHH:MM:SS"
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# Timestamp patterns to recognize
TIMESTAMP_PATTERNS = [
    # ISO 8601
    (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)', '%Y-%m-%dT%H:%M:%S'),
    # Common log format
    (r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)', '%Y-%m-%d %H:%M:%S'),
    # Syslog style
    (r'([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
]

# Event patterns that indicate significant incidents
EVENT_PATTERNS = {
    'error': re.compile(r'\b(ERROR|FATAL|CRITICAL)\b', re.IGNORECASE),
    'exception': re.compile(r'(Exception|Traceback|panic|SIGSEGV)', re.IGNORECASE),
    'deployment': re.compile(r'\b(deploy|deployed|release|version|upgrade)\b', re.IGNORECASE),
    'restart': re.compile(r'\b(restart|started|stopped|shutdown|init|boot)\b', re.IGNORECASE),
    'connection': re.compile(r'\b(connection|refused|timeout|unreachable|DNS)\b', re.IGNORECASE),
    'memory': re.compile(r'\b(OOM|OutOfMemory|heap|memory|GC)\b', re.IGNORECASE),
    'alert': re.compile(r'\b(alert|alarm|threshold|spike|anomaly)\b', re.IGNORECASE),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate incident timeline from log files'
    )
    parser.add_argument('log_path', help='Path to log file or directory')
    parser.add_argument(
        '--start',
        help='Start time (YYYY-MM-DDTHH:MM:SS)',
        default=None
    )
    parser.add_argument(
        '--end',
        help='End time (YYYY-MM-DDTHH:MM:SS)',
        default=None
    )
    parser.add_argument(
        '--max-events',
        type=int,
        default=100,
        help='Maximum events to include (default: 100)'
    )
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)',
        default=None
    )
    return parser.parse_args()


def parse_timestamp(line):
    """Extract timestamp from a log line."""
    for pattern, fmt in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            ts_str = match.group(1)
            # Handle timezone
            ts_str = re.sub(r'Z$', '+00:00', ts_str)
            ts_str = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', ts_str)
            # Remove milliseconds for parsing
            ts_str = re.sub(r'\.\d+', '', ts_str)
            # Remove timezone for simple parsing
            ts_str = re.sub(r'[+-]\d{2}:\d{2}$', '', ts_str)
            try:
                return datetime.strptime(ts_str.strip(), fmt)
            except ValueError:
                continue
    return None


def classify_event(line):
    """Classify an event based on patterns."""
    categories = []
    for category, pattern in EVENT_PATTERNS.items():
        if pattern.search(line):
            categories.append(category)
    return categories if categories else ['info']


def get_log_files(path):
    """Get all log files from path (file or directory)."""
    path = Path(path)
    
    if path.is_file():
        return [path]
    
    if path.is_dir():
        log_files = []
        for ext in ['*.log', '*.txt', '*.out']:
            log_files.extend(path.glob(ext))
            log_files.extend(path.glob(f'**/{ext}'))
        return sorted(set(log_files))
    
    print(f"Error: Path not found: {path}", file=sys.stderr)
    sys.exit(1)


def extract_events(log_files, start_time=None, end_time=None, max_events=100):
    """Extract significant events from log files."""
    events = []
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse timestamp
                    timestamp = parse_timestamp(line)
                    if not timestamp:
                        continue
                    
                    # Filter by time range
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    
                    # Classify event
                    categories = classify_event(line)
                    
                    # Skip non-significant events
                    if categories == ['info']:
                        continue
                    
                    events.append({
                        'timestamp': timestamp,
                        'file': str(log_file.name),
                        'line': line_num,
                        'categories': categories,
                        'content': line[:200],
                    })
        except Exception as e:
            print(f"Warning: Could not read {log_file}: {e}", file=sys.stderr)
    
    # Sort by timestamp and limit
    events.sort(key=lambda x: x['timestamp'])
    return events[:max_events]


def format_timeline(events):
    """Format events as markdown timeline."""
    if not events:
        return "No significant events found in the specified time range."
    
    output = []
    output.append("# Incident Timeline\n")
    output.append(f"**Events found:** {len(events)}\n")
    
    if events:
        output.append(f"**Time range:** {events[0]['timestamp']} to {events[-1]['timestamp']}\n")
    
    output.append("\n## Events\n")
    output.append("| Time (UTC) | Category | Source | Event |")
    output.append("|------------|----------|--------|-------|")
    
    for event in events:
        time_str = event['timestamp'].strftime('%H:%M:%S')
        categories = ', '.join(event['categories'])
        source = f"{event['file']}:{event['line']}"
        # Truncate content and escape pipe characters
        content = event['content'][:80].replace('|', '\\|')
        output.append(f"| {time_str} | {categories} | {source} | {content} |")
    
    # Add summary section
    output.append("\n## Summary\n")
    
    # Count by category
    category_counts = {}
    for event in events:
        for cat in event['categories']:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    output.append("### Event Categories\n")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        output.append(f"- **{cat}**: {count}")
    
    return "\n".join(output)


def main():
    args = parse_args()
    
    # Parse time range
    start_time = None
    end_time = None
    
    if args.start:
        try:
            start_time = datetime.fromisoformat(args.start.replace('Z', '+00:00'))
        except ValueError:
            print(f"Error: Invalid start time format: {args.start}", file=sys.stderr)
            sys.exit(1)
    
    if args.end:
        try:
            end_time = datetime.fromisoformat(args.end.replace('Z', '+00:00'))
        except ValueError:
            print(f"Error: Invalid end time format: {args.end}", file=sys.stderr)
            sys.exit(1)
    
    # Get log files
    log_files = get_log_files(args.log_path)
    
    if not log_files:
        print("No log files found.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzing {len(log_files)} log file(s)...", file=sys.stderr)
    
    # Extract events
    events = extract_events(log_files, start_time, end_time, args.max_events)
    
    # Format output
    timeline = format_timeline(events)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(timeline)
        print(f"Timeline written to {args.output}", file=sys.stderr)
    else:
        print(timeline)


if __name__ == '__main__':
    main()
