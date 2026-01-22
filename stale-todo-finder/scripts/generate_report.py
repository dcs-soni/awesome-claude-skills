#!/usr/bin/env python3
"""
Report Generator

Generate a markdown report of stale TODOs.
Usage: python generate_report.py <directory> [--output stale_todos.md]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_PATTERNS = ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG', 'OPTIMIZE']
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.c', '.cpp', '.h',
    '.hpp', '.cs', '.rb', '.rs', '.php', '.swift', '.kt', '.scala', '.sh'
}
SKIP_DIRS = {'node_modules', 'vendor', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build'}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate markdown report of stale TODOs'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Git repository directory'
    )
    parser.add_argument(
        '--output',
        default='stale_todos.md',
        help='Output file path'
    )
    parser.add_argument(
        '--min-age',
        type=int,
        default=0,
        help='Minimum age in days to include'
    )
    return parser.parse_args()


def is_git_repo(directory):
    return (Path(directory) / '.git').exists()


def git_blame_line(file_path, line_num, repo_root):
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
        
        author = None
        author_time = None
        
        for line in result.stdout.split('\n'):
            if line.startswith('author '):
                author = line[7:]
            elif line.startswith('author-time '):
                author_time = datetime.fromtimestamp(int(line[12:]))
        
        if author_time:
            return {
                'author': author,
                'date': author_time.strftime('%Y-%m-%d'),
                'age_days': (datetime.now() - author_time).days
            }
    except Exception:
        pass
    return None


def find_todos_in_file(file_path, patterns):
    todos = []
    pattern_regex = re.compile(r'\b(' + '|'.join(patterns) + r')\b[:\s]*(.*)$', re.IGNORECASE)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                match = pattern_regex.search(line)
                if match:
                    todos.append({
                        'line': line_num,
                        'pattern': match.group(1).upper(),
                        'content': match.group(2).strip()[:100]
                    })
    except Exception:
        pass
    return todos


def categorize_age(age_days):
    if age_days > 365:
        return 'ancient', '🔴'
    elif age_days > 180:
        return 'stale', '🟠'
    elif age_days > 90:
        return 'aging', '🟡'
    else:
        return 'recent', '🟢'


def collect_todos(directory, min_age):
    root_path = Path(directory).resolve()
    results = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() not in CODE_EXTENSIONS:
                continue
            
            todos = find_todos_in_file(file_path, DEFAULT_PATTERNS)
            
            for todo in todos:
                rel_path = file_path.relative_to(root_path)
                blame = git_blame_line(rel_path, todo['line'], root_path)
                
                if blame and blame['age_days'] >= min_age:
                    cat, emoji = categorize_age(blame['age_days'])
                    results.append({
                        'file': str(rel_path),
                        'line': todo['line'],
                        'pattern': todo['pattern'],
                        'content': todo['content'],
                        'author': blame['author'],
                        'date': blame['date'],
                        'age_days': blame['age_days'],
                        'category': cat,
                        'emoji': emoji
                    })
    
    results.sort(key=lambda x: -x['age_days'])
    return results


def generate_report(results, directory):
    """Generate markdown report."""
    lines = []
    lines.append("# Stale TODO Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Directory:** {directory}\n")
    
    # Summary
    categories = {'ancient': [], 'stale': [], 'aging': [], 'recent': []}
    for r in results:
        categories[r['category']].append(r)
    
    lines.append("## Summary\n")
    lines.append(f"| Category | Count |")
    lines.append(f"|----------|-------|")
    lines.append(f"| 🔴 Ancient (>1 year) | {len(categories['ancient'])} |")
    lines.append(f"| 🟠 Stale (6-12 months) | {len(categories['stale'])} |")
    lines.append(f"| 🟡 Aging (3-6 months) | {len(categories['aging'])} |")
    lines.append(f"| 🟢 Recent (<3 months) | {len(categories['recent'])} |")
    lines.append(f"| **Total** | **{len(results)}** |\n")
    
    # Details by category
    labels = {
        'ancient': '🔴 Ancient TODOs (>1 year)',
        'stale': '🟠 Stale TODOs (6-12 months)',
        'aging': '🟡 Aging TODOs (3-6 months)',
        'recent': '🟢 Recent TODOs (<3 months)'
    }
    
    for cat in ['ancient', 'stale', 'aging', 'recent']:
        items = categories[cat]
        if not items:
            continue
        
        lines.append(f"\n## {labels[cat]}\n")
        lines.append("| File | Line | Age | Author | Content |")
        lines.append("|------|------|-----|--------|---------|")
        
        for r in items:
            content = r['content'].replace('|', '\\|')[:50]
            lines.append(f"| {r['file']} | {r['line']} | {r['age_days']}d | {r['author']} | {content} |")
    
    # Recommendations
    if categories['ancient']:
        lines.append("\n## Recommendations\n")
        lines.append("### High Priority (Ancient TODOs)\n")
        lines.append("These TODOs are over a year old and likely forgotten:\n")
        for r in categories['ancient'][:5]:
            lines.append(f"- [ ] **{r['file']}:{r['line']}** - {r['content'][:60]}")
    
    return '\n'.join(lines)


def main():
    args = parse_args()
    root = Path(args.directory).resolve()
    
    if not is_git_repo(root):
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzing TODOs in {root}...", file=sys.stderr)
    results = collect_todos(root, args.min_age)
    
    report = generate_report(results, args.directory)
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report written to {output_path}", file=sys.stderr)
    print(f"Found {len(results)} TODOs", file=sys.stderr)


if __name__ == '__main__':
    main()
