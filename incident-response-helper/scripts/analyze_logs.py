#!/usr/bin/env python3
"""
Log Analysis Utility

Parses log files and identifies error patterns, exceptions, and anomalies.
Usage: python analyze_logs.py <log_file> [--format json|text]
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# Common log patterns
PATTERNS = {
    'error': re.compile(r'\b(ERROR|FATAL|CRITICAL)\b', re.IGNORECASE),
    'warning': re.compile(r'\bWARN(?:ING)?\b', re.IGNORECASE),
    'exception': re.compile(r'(Exception|Error|Traceback):', re.IGNORECASE),
    'http_status': re.compile(r'\b(HTTP[/\s]?\d\.\d\s+)?([4-5]\d{2})\b'),
    'timestamp': re.compile(
        r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'
    ),
    'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
    'latency_ms': re.compile(r'(\d+(?:\.\d+)?)\s*(?:ms|milliseconds?)', re.IGNORECASE),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Analyze log files for error patterns and anomalies'
    )
    parser.add_argument('log_file', help='Path to log file to analyze')
    parser.add_argument(
        '--format', 
        choices=['json', 'text'], 
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--tail',
        type=int,
        default=0,
        help='Only analyze last N lines (0 = all)'
    )
    return parser.parse_args()


def analyze_log_file(log_path, tail_lines=0):
    """Analyze a log file and return statistics."""
    
    results = {
        'file': str(log_path),
        'total_lines': 0,
        'error_count': 0,
        'warning_count': 0,
        'exception_count': 0,
        'errors_by_type': Counter(),
        'http_status_codes': Counter(),
        'latencies': [],
        'first_timestamp': None,
        'last_timestamp': None,
        'sample_errors': [],
        'ip_addresses': Counter(),
    }
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found: {log_path}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {log_path}", file=sys.stderr)
        sys.exit(1)
    
    # Apply tail if specified
    if tail_lines > 0:
        lines = lines[-tail_lines:]
    
    results['total_lines'] = len(lines)
    
    for line_num, line in enumerate(lines, 1):
        # Extract timestamp
        ts_match = PATTERNS['timestamp'].search(line)
        if ts_match:
            ts_str = ts_match.group(1)
            if not results['first_timestamp']:
                results['first_timestamp'] = ts_str
            results['last_timestamp'] = ts_str
        
        # Count errors
        if PATTERNS['error'].search(line):
            results['error_count'] += 1
            # Extract error type if present
            exc_match = PATTERNS['exception'].search(line)
            if exc_match:
                results['errors_by_type'][exc_match.group(0)] += 1
            # Store sample (max 10)
            if len(results['sample_errors']) < 10:
                results['sample_errors'].append({
                    'line': line_num,
                    'content': line.strip()[:200]
                })
        
        # Count warnings
        if PATTERNS['warning'].search(line):
            results['warning_count'] += 1
        
        # Count exceptions
        if PATTERNS['exception'].search(line):
            results['exception_count'] += 1
        
        # Extract HTTP status codes
        status_match = PATTERNS['http_status'].search(line)
        if status_match:
            status_code = status_match.group(2)
            results['http_status_codes'][status_code] += 1
        
        # Extract latencies
        latency_match = PATTERNS['latency_ms'].search(line)
        if latency_match:
            try:
                latency = float(latency_match.group(1))
                results['latencies'].append(latency)
            except ValueError:
                pass
        
        # Count IP addresses
        ip_match = PATTERNS['ip_address'].search(line)
        if ip_match:
            results['ip_addresses'][ip_match.group(0)] += 1
    
    # Calculate latency stats
    if results['latencies']:
        latencies = results['latencies']
        results['latency_stats'] = {
            'min': min(latencies),
            'max': max(latencies),
            'avg': sum(latencies) / len(latencies),
            'count': len(latencies),
            'p50': sorted(latencies)[len(latencies) // 2],
            'p95': sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else None,
        }
    else:
        results['latency_stats'] = None
    
    # Convert counters for JSON serialization
    results['errors_by_type'] = dict(results['errors_by_type'].most_common(10))
    results['http_status_codes'] = dict(results['http_status_codes'].most_common(10))
    results['top_ips'] = dict(results['ip_addresses'].most_common(5))
    del results['ip_addresses']
    del results['latencies']
    
    return results


def format_text(results):
    """Format results as human-readable text."""
    
    output = []
    output.append("=" * 60)
    output.append(f"LOG ANALYSIS: {results['file']}")
    output.append("=" * 60)
    output.append("")
    
    # Summary
    output.append("## Summary")
    output.append(f"  Total lines:    {results['total_lines']:,}")
    output.append(f"  Errors:         {results['error_count']:,}")
    output.append(f"  Warnings:       {results['warning_count']:,}")
    output.append(f"  Exceptions:     {results['exception_count']:,}")
    output.append("")
    
    # Time range
    if results['first_timestamp']:
        output.append("## Time Range")
        output.append(f"  First: {results['first_timestamp']}")
        output.append(f"  Last:  {results['last_timestamp']}")
        output.append("")
    
    # HTTP Status Codes
    if results['http_status_codes']:
        output.append("## HTTP Status Codes (4xx/5xx)")
        for code, count in results['http_status_codes'].items():
            output.append(f"  {code}: {count:,}")
        output.append("")
    
    # Error types
    if results['errors_by_type']:
        output.append("## Error Types")
        for err_type, count in results['errors_by_type'].items():
            output.append(f"  {err_type}: {count:,}")
        output.append("")
    
    # Latency stats
    if results['latency_stats']:
        stats = results['latency_stats']
        output.append("## Latency (ms)")
        output.append(f"  Min:    {stats['min']:.2f}")
        output.append(f"  Max:    {stats['max']:.2f}")
        output.append(f"  Avg:    {stats['avg']:.2f}")
        output.append(f"  P50:    {stats['p50']:.2f}")
        if stats['p95']:
            output.append(f"  P95:    {stats['p95']:.2f}")
        output.append("")
    
    # Sample errors
    if results['sample_errors']:
        output.append("## Sample Errors (first 10)")
        for i, err in enumerate(results['sample_errors'], 1):
            output.append(f"  [{err['line']}] {err['content'][:100]}...")
        output.append("")
    
    return "\n".join(output)


def main():
    args = parse_args()
    log_path = Path(args.log_file)
    
    results = analyze_log_file(log_path, args.tail)
    
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == '__main__':
    main()
