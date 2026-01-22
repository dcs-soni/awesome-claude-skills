#!/usr/bin/env python3
"""
Empty Catch Block Finder

Find empty catch blocks and silent error handlers across multiple languages.
Usage: python find_empty_catches.py <directory> [--format json|text]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Language configurations
LANGUAGES = {
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.py': 'python',
    '.java': 'java',
    '.go': 'go',
    '.cs': 'csharp',
}

# Patterns for each language
PATTERNS = {
    'javascript': [
        # Empty catch: catch (e) {} or catch {}
        (r'catch\s*\([^)]*\)\s*\{\s*\}', 'empty_catch'),
        (r'catch\s*\{\s*\}', 'empty_catch'),
        # Comment-only catch
        (r'catch\s*\([^)]*\)\s*\{\s*(?://[^\n]*|/\*[^*]*\*/)\s*\}', 'comment_only'),
        # Silent return
        (r'catch\s*\([^)]*\)\s*\{\s*return\s*(?:null|undefined|false)?\s*;?\s*\}', 'silent_return'),
    ],
    'typescript': [
        (r'catch\s*\([^)]*\)\s*\{\s*\}', 'empty_catch'),
        (r'catch\s*\{\s*\}', 'empty_catch'),
        (r'catch\s*\([^)]*\)\s*\{\s*(?://[^\n]*|/\*[^*]*\*/)\s*\}', 'comment_only'),
        (r'catch\s*\([^)]*\)\s*\{\s*return\s*(?:null|undefined|false)?\s*;?\s*\}', 'silent_return'),
    ],
    'python': [
        # except: pass
        (r'except\s*:\s*pass', 'bare_except_pass'),
        # except Exception: pass
        (r'except\s+\w+(?:\s+as\s+\w+)?:\s*pass', 'exception_pass'),
        # except Exception: ... (ellipsis)
        (r'except\s+\w+(?:\s+as\s+\w+)?:\s*\.\.\.', 'exception_ellipsis'),
    ],
    'java': [
        # Empty catch
        (r'catch\s*\([^)]+\)\s*\{\s*\}', 'empty_catch'),
        # Comment-only
        (r'catch\s*\([^)]+\)\s*\{\s*(?://[^\n]*|/\*[^*]*\*/)\s*\}', 'comment_only'),
    ],
    'go': [
        # Ignored error with underscore
        (r',\s*_\s*:?=\s*\w+\([^)]*\)', 'ignored_error'),
        # Empty if err != nil
        (r'if\s+err\s*!=\s*nil\s*\{\s*\}', 'empty_error_check'),
    ],
    'csharp': [
        # Empty catch
        (r'catch\s*(?:\([^)]*\))?\s*\{\s*\}', 'empty_catch'),
        # Catch-all empty
        (r'catch\s*\{\s*\}', 'catch_all_empty'),
    ],
}

# Risk keywords
HIGH_RISK_KEYWORDS = ['async', 'await', 'database', 'db', 'sql', 'payment', 'transaction', 'save', 'write', 'delete']
MEDIUM_RISK_KEYWORDS = ['api', 'request', 'response', 'fetch', 'http']
LOW_RISK_INDICATORS = ['test', 'spec', 'mock', '__test__', 'intentional', 'expected']

SKIP_DIRS = {'node_modules', 'vendor', 'venv', '.venv', '__pycache__', '.git', 'dist', 'build'}


def parse_args():
    parser = argparse.ArgumentParser(description='Find empty catch blocks')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan')
    parser.add_argument('--format', choices=['json', 'text'], default='text')
    parser.add_argument('--include-low-risk', action='store_true', help='Include low risk items')
    return parser.parse_args()


def get_language(file_path):
    """Determine language from file extension."""
    return LANGUAGES.get(file_path.suffix.lower())


def assess_risk(file_path, line_content, context_lines):
    """Assess risk level of empty catch."""
    file_str = str(file_path).lower()
    content_lower = line_content.lower()
    context_lower = ' '.join(context_lines).lower()
    
    # Low risk indicators
    for indicator in LOW_RISK_INDICATORS:
        if indicator in file_str or indicator in content_lower:
            return 'low', 'In test/intentional context'
    
    # High risk
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in context_lower or keyword in file_str:
            return 'critical', f'Found in {keyword} context'
    
    # Medium risk
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in context_lower or keyword in file_str:
            return 'high', f'Found in {keyword} context'
    
    return 'medium', 'General code'


def find_empty_catches_in_file(file_path, language):
    """Find empty catches in a single file."""
    findings = []
    patterns = PATTERNS.get(language, [])
    
    if not patterns:
        return findings
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return findings
    
    for pattern, pattern_type in patterns:
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            
            # Get context (5 lines before and after)
            start_line = max(0, line_num - 5)
            end_line = min(len(lines), line_num + 5)
            context_lines = lines[start_line:end_line]
            
            matched_text = match.group(0)[:100]
            risk_level, risk_reason = assess_risk(file_path, matched_text, context_lines)
            
            findings.append({
                'file': str(file_path),
                'line': line_num,
                'type': pattern_type,
                'language': language,
                'content': matched_text.strip(),
                'risk': risk_level,
                'risk_reason': risk_reason,
            })
    
    return findings


def find_all_empty_catches(directory, include_low_risk=False):
    """Find all empty catches in directory."""
    findings = []
    root_path = Path(directory).resolve()
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            language = get_language(file_path)
            
            if not language:
                continue
            
            file_findings = find_empty_catches_in_file(file_path, language)
            
            for finding in file_findings:
                finding['file'] = str(file_path.relative_to(root_path))
                
                if not include_low_risk and finding['risk'] == 'low':
                    continue
                
                findings.append(finding)
    
    # Sort by risk (critical first)
    risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    findings.sort(key=lambda x: risk_order.get(x['risk'], 99))
    
    return findings


def format_text(findings):
    """Format findings as text."""
    if not findings:
        return "No empty catch blocks found."
    
    output = []
    output.append(f"Found {len(findings)} empty catch blocks\n")
    
    # Group by risk
    by_risk = {'critical': [], 'high': [], 'medium': [], 'low': []}
    for f in findings:
        by_risk[f['risk']].append(f)
    
    labels = {
        'critical': '[CRITICAL]',
        'high': '[HIGH]',
        'medium': '[MEDIUM]',
        'low': '[LOW]'
    }
    
    for risk in ['critical', 'high', 'medium', 'low']:
        items = by_risk[risk]
        if items:
            output.append(f"\n{labels[risk]} ({len(items)})\n")
            for f in items:
                output.append(f"  {f['file']}:{f['line']}")
                output.append(f"    Type: {f['type']} | {f['risk_reason']}")
                output.append(f"    Code: {f['content'][:60]}")
    
    return '\n'.join(output)


def main():
    args = parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning {directory}...", file=sys.stderr)
    findings = find_all_empty_catches(directory, args.include_low_risk)
    
    if args.format == 'json':
        print(json.dumps(findings, indent=2))
    else:
        print(format_text(findings))


if __name__ == '__main__':
    main()
