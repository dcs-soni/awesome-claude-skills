#!/usr/bin/env python3
"""
Generate PR Description

Generate a structured Pull Request description from git changes.
Usage: python generate_description.py --base main --output pr.md
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description='Generate PR description')
    parser.add_argument('--base', default='main', help='Base branch (default: main)')
    parser.add_argument('--output', help='Output file (default: stdout)')
    parser.add_argument('--title', help='PR title (auto-generated if not provided)')
    return parser.parse_args()


def run_git(args):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.returncode == 0
    except Exception:
        return '', False


def get_analysis(base):
    """Get change analysis (reusing logic from analyze_changes.py)."""
    
    # Get merge base
    merge_base_out, _ = run_git(['merge-base', base, 'HEAD'])
    merge_base = merge_base_out if merge_base_out else base
    
    # Get commits
    commits_out, _ = run_git([
        'log', f'{merge_base}..HEAD',
        '--pretty=format:%H|%s|%an',
        '--reverse'
    ])
    
    commits = []
    if commits_out:
        for line in commits_out.split('\n'):
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) >= 2:
                    commits.append({
                        'hash': parts[0][:8],
                        'message': parts[1],
                        'author': parts[2] if len(parts) > 2 else 'Unknown'
                    })
    
    # Get file changes
    files_out, _ = run_git(['diff', '--name-status', merge_base, 'HEAD'])
    file_changes = []
    if files_out:
        for line in files_out.split('\n'):
            if '\t' in line:
                parts = line.split('\t')
                status = {'A': 'Added', 'M': 'Modified', 'D': 'Deleted', 'R': 'Renamed'}.get(parts[0][0], parts[0])
                file_changes.append({'status': status, 'file': parts[-1]})
    
    # Get stats
    stats_out, _ = run_git(['diff', '--stat', merge_base, 'HEAD'])
    stats = {'files': len(file_changes), 'insertions': 0, 'deletions': 0}
    if stats_out:
        last_line = stats_out.strip().split('\n')[-1]
        ins = re.search(r'(\d+)\s+insertions?', last_line)
        dels = re.search(r'(\d+)\s+deletions?', last_line)
        if ins: stats['insertions'] = int(ins.group(1))
        if dels: stats['deletions'] = int(dels.group(1))
    
    # Extract issues
    issues = set()
    for c in commits:
        matches = re.findall(r'#(\d+)', c['message'])
        issues.update(matches)
    
    # Detect type
    msgs = ' '.join([c['message'].lower() for c in commits])
    pr_type = 'feature'
    if re.search(r'\bfix[:\(]', msgs): pr_type = 'bugfix'
    elif re.search(r'\brefactor[:\(]', msgs): pr_type = 'refactor'
    elif re.search(r'\bdocs?[:\(]', msgs): pr_type = 'docs'
    elif re.search(r'\bchore[:\(]', msgs): pr_type = 'chore'
    
    # Detect breaking
    breaking = 'breaking' in msgs or '!:' in msgs
    
    return {
        'commits': commits,
        'file_changes': file_changes,
        'stats': stats,
        'issues': sorted(issues, key=lambda x: int(x)),
        'pr_type': pr_type,
        'breaking': breaking
    }


def generate_title(commits, pr_type):
    """Generate a PR title from commits."""
    if not commits:
        return "Update"
    
    # Use first commit message, cleaned up
    first = commits[0]['message']
    
    # Remove conventional commit prefix for title
    title = re.sub(r'^(feat|fix|docs|refactor|chore|test|perf)(\([^)]+\))?:\s*', '', first)
    
    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]
    
    return title[:72]  # GitHub title limit


def generate_summary(commits, pr_type):
    """Generate a summary paragraph."""
    if not commits:
        return "[Describe what this PR does]"
    
    # Collect all commit messages
    messages = [c['message'] for c in commits]
    
    # Simple approach: use the first commit if only one, otherwise summarize
    if len(messages) == 1:
        return messages[0]
    
    # For multiple commits, create a summary
    type_verb = {
        'feature': 'Adds',
        'bugfix': 'Fixes',
        'refactor': 'Refactors',
        'docs': 'Updates documentation for',
        'chore': 'Updates'
    }
    
    verb = type_verb.get(pr_type, 'Implements')
    
    # Try to find a common theme
    return f"{verb} {messages[0].lower()}"


def generate_changes_list(commits, file_changes):
    """Generate a bullet list of changes."""
    changes = []
    
    # Group commits by type
    for commit in commits:
        msg = commit['message']
        # Clean up conventional commit prefix
        clean = re.sub(r'^(feat|fix|docs|refactor|chore|test|perf)(\([^)]+\))?:\s*', '', msg)
        if clean and clean not in changes:
            changes.append(clean)
    
    return changes[:10]  # Limit to 10 items


def generate_testing_instructions(pr_type, file_changes):
    """Generate testing instructions based on PR type."""
    if pr_type == 'docs':
        return ["Review the documentation changes for accuracy", "Verify links work correctly"]
    
    if pr_type == 'bugfix':
        return [
            "Verify the bug is fixed by [describe steps]",
            "Confirm no regression in related functionality"
        ]
    
    # Default feature testing
    return [
        "[Step 1: How to test this change]",
        "[Step 2: What to verify]",
        "[Step 3: Edge cases to check]"
    ]


def generate_description(analysis, title=None):
    """Generate the full PR description markdown."""
    
    lines = []
    
    # Title (if not provided separately)
    if title:
        lines.append(f"# {title}\n")
    
    # Summary
    summary = generate_summary(analysis['commits'], analysis['pr_type'])
    lines.append("## Summary")
    lines.append(f"{summary}\n")
    
    # Type of Change
    lines.append("## Type of Change")
    type_map = {
        'feature': '✨ New feature',
        'bugfix': '🐛 Bug fix',
        'refactor': '♻️ Refactoring',
        'docs': '📝 Documentation',
        'chore': '🔧 Chore/Maintenance'
    }
    
    for key, label in type_map.items():
        checked = 'x' if key == analysis['pr_type'] else ' '
        lines.append(f"- [{checked}] {label}")
    
    if analysis['breaking']:
        lines.append("- [x] 💥 **Breaking change**")
    
    lines.append("")
    
    # Changes Made
    lines.append("## Changes Made")
    changes = generate_changes_list(analysis['commits'], analysis['file_changes'])
    for change in changes:
        lines.append(f"- {change}")
    lines.append("")
    
    # Files Changed
    if analysis['file_changes']:
        lines.append("## Files Changed")
        lines.append("| Status | File |")
        lines.append("|--------|------|")
        for f in analysis['file_changes'][:15]:  # Limit display
            lines.append(f"| {f['status']} | `{f['file']}` |")
        if len(analysis['file_changes']) > 15:
            lines.append(f"| ... | +{len(analysis['file_changes']) - 15} more files |")
        lines.append("")
    
    # Testing Instructions
    lines.append("## Testing Instructions")
    testing = generate_testing_instructions(analysis['pr_type'], analysis['file_changes'])
    for i, step in enumerate(testing, 1):
        lines.append(f"{i}. {step}")
    lines.append("")
    
    # Related Issues
    if analysis['issues']:
        lines.append("## Related Issues")
        issue_refs = ', '.join([f"#{i}" for i in analysis['issues']])
        lines.append(f"Closes {issue_refs}\n")
    
    # Checklist
    lines.append("## Checklist")
    lines.append("- [ ] Tests added/updated")
    lines.append("- [ ] Documentation updated")
    lines.append("- [ ] No breaking changes (or migration guide provided)")
    lines.append("- [ ] Self-reviewed the code")
    lines.append("")
    
    # Stats footer
    stats = analysis['stats']
    lines.append("---")
    lines.append(f"*{stats['files']} files changed, +{stats['insertions']} insertions, -{stats['deletions']} deletions*")
    
    return '\n'.join(lines)


def main():
    args = parse_args()
    
    # Check if in git repo
    _, is_git = run_git(['rev-parse', '--git-dir'])
    if not is_git:
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    # Get analysis
    print(f"Analyzing changes against {args.base}...", file=sys.stderr)
    analysis = get_analysis(args.base)
    
    if not analysis['commits']:
        print(f"No commits found between {args.base} and HEAD", file=sys.stderr)
        print("Make sure you have commits on your branch.", file=sys.stderr)
        sys.exit(1)
    
    # Generate title if not provided
    title = args.title or generate_title(analysis['commits'], analysis['pr_type'])
    
    # Generate description
    description = generate_description(analysis, title)
    
    # Output
    if args.output:
        Path(args.output).write_text(description, encoding='utf-8')
        print(f"PR description written to {args.output}", file=sys.stderr)
        print(f"Title suggestion: {title}", file=sys.stderr)
    else:
        print(description)


if __name__ == '__main__':
    main()
