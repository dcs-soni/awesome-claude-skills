#!/usr/bin/env python3
"""
Analyze Changes

Parse git diff and commit history to understand what changed.
Usage: python analyze_changes.py --base main
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze git changes for PR description')
    parser.add_argument('--base', default='main', help='Base branch to compare against (default: main)')
    parser.add_argument('--format', choices=['json', 'text'], default='text')
    return parser.parse_args()


def run_git(args, cwd=None):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return result.stdout.strip(), result.returncode == 0
    except Exception as e:
        return str(e), False


def get_current_branch():
    """Get the current branch name."""
    output, success = run_git(['branch', '--show-current'])
    return output if success else 'HEAD'


def get_merge_base(base_branch):
    """Find the common ancestor between current branch and base."""
    output, success = run_git(['merge-base', base_branch, 'HEAD'])
    return output if success else base_branch


def get_commits(base_ref):
    """Get commits between base and HEAD."""
    output, success = run_git([
        'log', f'{base_ref}..HEAD',
        '--pretty=format:%H|%s|%an|%ae',
        '--reverse'
    ])
    
    if not success or not output:
        return []
    
    commits = []
    for line in output.split('\n'):
        if '|' in line:
            parts = line.split('|', 3)
            if len(parts) >= 2:
                commits.append({
                    'hash': parts[0][:8],
                    'message': parts[1],
                    'author': parts[2] if len(parts) > 2 else 'Unknown',
                    'email': parts[3] if len(parts) > 3 else ''
                })
    return commits


def get_file_changes(base_ref):
    """Get list of changed files with status."""
    output, success = run_git(['diff', '--name-status', base_ref, 'HEAD'])
    
    if not success or not output:
        return []
    
    changes = []
    for line in output.split('\n'):
        if '\t' in line:
            parts = line.split('\t')
            status = parts[0][0]  # First char: A, M, D, R
            filename = parts[-1]
            
            status_map = {'A': 'Added', 'M': 'Modified', 'D': 'Deleted', 'R': 'Renamed'}
            changes.append({
                'status': status_map.get(status, status),
                'file': filename
            })
    return changes


def get_diff_stats(base_ref):
    """Get diff statistics (lines added/removed)."""
    output, success = run_git(['diff', '--stat', base_ref, 'HEAD'])
    
    stats = {'files': 0, 'insertions': 0, 'deletions': 0}
    
    if success and output:
        # Parse last line like: "5 files changed, 120 insertions(+), 30 deletions(-)"
        lines = output.strip().split('\n')
        if lines:
            last_line = lines[-1]
            
            files_match = re.search(r'(\d+)\s+files?\s+changed', last_line)
            if files_match:
                stats['files'] = int(files_match.group(1))
            
            ins_match = re.search(r'(\d+)\s+insertions?\(\+\)', last_line)
            if ins_match:
                stats['insertions'] = int(ins_match.group(1))
            
            del_match = re.search(r'(\d+)\s+deletions?\(-\)', last_line)
            if del_match:
                stats['deletions'] = int(del_match.group(1))
    
    return stats


def extract_issue_references(commits):
    """Extract issue references from commit messages."""
    issues = set()
    # Patterns: #123, fixes #123, closes #123, resolves #123
    pattern = re.compile(r'(?:fixes?|closes?|resolves?|refs?)?\s*#(\d+)', re.IGNORECASE)
    
    for commit in commits:
        matches = pattern.findall(commit['message'])
        issues.update(matches)
    
    return sorted(issues, key=int)


def detect_pr_type(commits, file_changes):
    """Detect the type of PR based on commits and files."""
    commit_messages = ' '.join([c['message'].lower() for c in commits])
    
    # Check conventional commit prefixes
    if re.search(r'\bfix[:\(]|\bbug[:\(]', commit_messages):
        return 'bugfix'
    if re.search(r'\bfeat[:\(]|\bfeature[:\(]', commit_messages):
        return 'feature'
    if re.search(r'\brefactor[:\(]', commit_messages):
        return 'refactor'
    if re.search(r'\bdocs?[:\(]', commit_messages):
        return 'docs'
    if re.search(r'\bchore[:\(]|\bci[:\(]|\bbuild[:\(]', commit_messages):
        return 'chore'
    
    # Check file types
    extensions = defaultdict(int)
    for change in file_changes:
        ext = Path(change['file']).suffix.lower()
        extensions[ext] += 1
    
    # If mostly markdown, it's docs
    md_count = extensions.get('.md', 0)
    total = len(file_changes)
    if total > 0 and md_count / total > 0.8:
        return 'docs'
    
    # If has new files, likely feature
    added = sum(1 for c in file_changes if c['status'] == 'Added')
    if added > 0:
        return 'feature'
    
    return 'feature'  # Default


def detect_breaking_changes(commits, file_changes):
    """Detect if there are breaking changes."""
    indicators = []
    
    # Check commit messages
    for commit in commits:
        msg = commit['message'].lower()
        if 'breaking' in msg or 'breaking change' in msg:
            indicators.append(f"Commit mentions breaking change: {commit['message'][:50]}")
        if msg.startswith('!') or '!:' in msg:
            indicators.append(f"Commit uses breaking change syntax: {commit['message'][:50]}")
    
    # Check for API/schema file changes
    breaking_patterns = ['api', 'schema', 'migration', 'types', 'interface']
    for change in file_changes:
        for pattern in breaking_patterns:
            if pattern in change['file'].lower():
                indicators.append(f"Changed {pattern} file: {change['file']}")
    
    return indicators


def main():
    args = parse_args()
    
    # Check if in git repo
    _, is_git = run_git(['rev-parse', '--git-dir'])
    if not is_git:
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    # Get base reference
    merge_base = get_merge_base(args.base)
    current_branch = get_current_branch()
    
    # Gather data
    commits = get_commits(merge_base)
    file_changes = get_file_changes(merge_base)
    diff_stats = get_diff_stats(merge_base)
    issues = extract_issue_references(commits)
    pr_type = detect_pr_type(commits, file_changes)
    breaking = detect_breaking_changes(commits, file_changes)
    
    result = {
        'base_branch': args.base,
        'current_branch': current_branch,
        'merge_base': merge_base[:8] if len(merge_base) > 8 else merge_base,
        'commits': commits,
        'file_changes': file_changes,
        'stats': diff_stats,
        'issues': issues,
        'pr_type': pr_type,
        'breaking_changes': breaking,
    }
    
    if args.format == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(f"PR Analysis: {current_branch} → {args.base}")
        print("=" * 60)
        print(f"\nType: {pr_type.upper()}")
        print(f"Commits: {len(commits)}")
        print(f"Files: {diff_stats['files']} changed, +{diff_stats['insertions']} -{diff_stats['deletions']}")
        
        if issues:
            print(f"Related Issues: {', '.join(['#' + i for i in issues])}")
        
        if breaking:
            print(f"\n⚠️  POSSIBLE BREAKING CHANGES:")
            for b in breaking:
                print(f"  - {b}")
        
        print(f"\nCommits:")
        for c in commits:
            print(f"  {c['hash']} {c['message'][:60]}")
        
        print(f"\nFiles Changed:")
        for f in file_changes:
            print(f"  [{f['status'][:1]}] {f['file']}")


if __name__ == '__main__':
    main()
