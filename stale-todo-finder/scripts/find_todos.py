#!/usr/bin/env python3
"""
TODO Finder

Find all TODO-style comments in a codebase.
Usage: python find_todos.py <directory> [--format json|text] [--patterns TODO,FIXME]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Default patterns to search for
DEFAULT_PATTERNS = ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG', 'OPTIMIZE']

# File extensions to search
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.c', '.cpp', '.h',
    '.hpp', '.cs', '.rb', '.rs', '.php', '.swift', '.kt', '.scala', '.sh',
    '.yaml', '.yml', '.sql', '.vue', '.svelte'
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', 'vendor', 'venv', '.venv', '__pycache__', '.git',
    'dist', 'build', '.next', 'target', 'bin', 'obj', '.idea', '.vscode'
}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Find TODO-style comments in codebase'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to search (default: current)'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--patterns',
        default=','.join(DEFAULT_PATTERNS),
        help=f'Comma-separated patterns (default: {",".join(DEFAULT_PATTERNS)})'
    )
    parser.add_argument(
        '--exclude',
        default='',
        help='Comma-separated glob patterns to exclude'
    )
    return parser.parse_args()


def should_skip_dir(dir_name):
    """Check if directory should be skipped."""
    return dir_name in SKIP_DIRS or dir_name.startswith('.')


def is_code_file(file_path):
    """Check if file is a code file."""
    return file_path.suffix.lower() in CODE_EXTENSIONS


def find_todos_in_file(file_path, patterns):
    """Find TODO comments in a single file."""
    todos = []
    pattern_regex = re.compile(
        r'(?:#|//|/\*|\*|--|<!--|\'\'\'|""")?\s*\b(' + '|'.join(patterns) + r')\b[:\s]*(.*)$',
        re.IGNORECASE
    )
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                match = pattern_regex.search(line)
                if match:
                    pattern = match.group(1).upper()
                    content = match.group(2).strip()
                    # Clean up content
                    content = re.sub(r'\s*(\*/|-->|\'\'\'|""")?\s*$', '', content)
                    
                    todos.append({
                        'file': str(file_path),
                        'line': line_num,
                        'pattern': pattern,
                        'content': content[:200],
                        'raw_line': line.strip()[:300]
                    })
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
    
    return todos


def find_all_todos(directory, patterns, exclude_patterns):
    """Find all TODOs in directory."""
    todos = []
    root_path = Path(directory).resolve()
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            
            if not is_code_file(file_path):
                continue
            
            # Check exclude patterns
            rel_path = file_path.relative_to(root_path)
            skip = False
            for exclude in exclude_patterns:
                if rel_path.match(exclude):
                    skip = True
                    break
            if skip:
                continue
            
            file_todos = find_todos_in_file(file_path, patterns)
            for todo in file_todos:
                todo['file'] = str(rel_path)
            todos.extend(file_todos)
    
    return todos


def format_text(todos):
    """Format todos as text."""
    if not todos:
        return "No TODO comments found."
    
    output = []
    output.append(f"Found {len(todos)} TODO comments\n")
    output.append("=" * 60)
    
    # Group by pattern
    by_pattern = {}
    for todo in todos:
        pattern = todo['pattern']
        if pattern not in by_pattern:
            by_pattern[pattern] = []
        by_pattern[pattern].append(todo)
    
    for pattern, items in sorted(by_pattern.items()):
        output.append(f"\n## {pattern} ({len(items)})\n")
        for todo in items:
            output.append(f"  {todo['file']}:{todo['line']}")
            output.append(f"    {todo['content'][:80]}")
    
    return '\n'.join(output)


def main():
    args = parse_args()
    
    patterns = [p.strip().upper() for p in args.patterns.split(',')]
    exclude_patterns = [p.strip() for p in args.exclude.split(',') if p.strip()]
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)
    
    todos = find_all_todos(directory, patterns, exclude_patterns)
    
    if args.format == 'json':
        print(json.dumps(todos, indent=2))
    else:
        print(format_text(todos))


if __name__ == '__main__':
    main()
