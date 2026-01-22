#!/usr/bin/env python3
"""
Staleness Analyzer

Analyze TODO comments using git blame to determine age.
Usage: python analyze_staleness.py <directory> [--min-age 90]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Import find_todos functionality
DEFAULT_PATTERNS = ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG', 'OPTIMIZE']
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.c', '.cpp', '.h',
    '.hpp', '.cs', '.rb', '.rs', '.php', '.swift', '.kt', '.scala', '.sh'
}
SKIP_DIRS = {'node_modules', 'vendor', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build'}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Analyze staleness of TODO comments using git blame'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Git repository directory (default: current)'
    )
    parser.add_argument(
        '--min-age',
        type=int,
        default=0,
        help='Only show TODOs older than N days'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--patterns',
        default=','.join(DEFAULT_PATTERNS),
        help='Comma-separated patterns to search'
    )
    return parser.parse_args()


def is_git_repo(directory):
    """Check if directory is a git repository."""
    git_dir = Path(directory) / '.git'
    return git_dir.exists()


def git_blame_line(file_path, line_num, repo_root):
    """Get git blame info for a specific line."""
    try:
        result = subprocess.run(
            ['git', 'blame', '-L', f'{line_num},{line_num}', '--porcelain', str(file_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        output = result.stdout
        
        # Parse porcelain output
        commit_hash = None
        author = None
        author_time = None
        
        for line in output.split('\n'):
            if re.match(r'^[0-9a-f]{40}', line):
                commit_hash = line.split()[0]
            elif line.startswith('author '):
                author = line[7:]
            elif line.startswith('author-time '):
                timestamp = int(line[12:])
                author_time = datetime.fromtimestamp(timestamp)
        
        if author_time:
            age_days = (datetime.now() - author_time).days
            return {
                'commit': commit_hash[:8] if commit_hash else None,
                'author': author,
                'date': author_time.strftime('%Y-%m-%d'),
                'age_days': age_days
            }
    except subprocess.TimeoutExpired:
        print(f"Warning: git blame timeout for {file_path}:{line_num}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: git blame failed for {file_path}:{line_num}: {e}", file=sys.stderr)
    
    return None


def find_todos_in_file(file_path, patterns):
    """Find TODO comments in a file."""
    todos = []
    pattern_regex = re.compile(
        r'\b(' + '|'.join(patterns) + r')\b[:\s]*(.*)$',
        re.IGNORECASE
    )
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                match = pattern_regex.search(line)
                if match:
                    todos.append({
                        'file': str(file_path),
                        'line': line_num,
                        'pattern': match.group(1).upper(),
                        'content': match.group(2).strip()[:150]
                    })
    except Exception:
        pass
    
    return todos


def categorize_age(age_days):
    """Categorize TODO by age."""
    if age_days > 365:
        return 'ancient'
    elif age_days > 180:
        return 'stale'
    elif age_days > 90:
        return 'aging'
    else:
        return 'recent'


def analyze_todos(directory, patterns, min_age):
    """Find TODOs and analyze their staleness."""
    root_path = Path(directory).resolve()
    
    if not is_git_repo(root_path):
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    results = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() not in CODE_EXTENSIONS:
                continue
            
            todos = find_todos_in_file(file_path, patterns)
            
            for todo in todos:
                rel_path = file_path.relative_to(root_path)
                blame_info = git_blame_line(rel_path, todo['line'], root_path)
                
                if blame_info:
                    if min_age > 0 and blame_info['age_days'] < min_age:
                        continue
                    
                    results.append({
                        'file': str(rel_path),
                        'line': todo['line'],
                        'pattern': todo['pattern'],
                        'content': todo['content'],
                        'author': blame_info['author'],
                        'date': blame_info['date'],
                        'age_days': blame_info['age_days'],
                        'category': categorize_age(blame_info['age_days'])
                    })
    
    # Sort by age (oldest first)
    results.sort(key=lambda x: -x['age_days'])
    return results


def format_text(results):
    """Format results as text."""
    if not results:
        return "No TODO comments found matching criteria."
    
    output = []
    output.append(f"Found {len(results)} TODO comments\n")
    
    # Group by category
    categories = {'ancient': [], 'stale': [], 'aging': [], 'recent': []}
    for r in results:
        categories[r['category']].append(r)
    
    labels = {
        'ancient': '🔴 Ancient (>1 year)',
        'stale': '🟠 Stale (6-12 months)',
        'aging': '🟡 Aging (3-6 months)',
        'recent': '🟢 Recent (<3 months)'
    }
    
    for cat in ['ancient', 'stale', 'aging', 'recent']:
        items = categories[cat]
        if items:
            output.append(f"\n## {labels[cat]} - {len(items)} found\n")
            for r in items:
                output.append(f"  {r['file']}:{r['line']} ({r['age_days']} days)")
                output.append(f"    {r['pattern']}: {r['content'][:60]}")
                output.append(f"    Author: {r['author']} | Date: {r['date']}")
    
    return '\n'.join(output)


def main():
    args = parse_args()
    patterns = [p.strip().upper() for p in args.patterns.split(',')]
    
    print(f"Analyzing TODOs in {args.directory}...", file=sys.stderr)
    results = analyze_todos(args.directory, patterns, args.min_age)
    
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == '__main__':
    main()
