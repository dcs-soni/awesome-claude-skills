#!/usr/bin/env python3
"""
Fix Suggestion Generator

Generate fix suggestions for empty catch blocks.
Usage: python generate_fixes.py <directory> [--output fixes.md]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Fix templates by language and type
FIX_TEMPLATES = {
    'javascript': {
        'empty_catch': '''// Before
catch (error) {{}}

// After - Option 1: Log and re-throw
catch (error) {{
  console.error('Operation failed:', error);
  throw error;
}}

// After - Option 2: Log and handle
catch (error) {{
  logger.error('Operation failed', {{ error, context: {{ /* add context */ }} }});
  // Handle gracefully or return error state
}}''',
        'silent_return': '''// Before
catch (error) {{
  return null;
}}

// After - Return error information
catch (error) {{
  logger.error('Operation failed', {{ error }});
  return {{ success: false, error: error.message }};
}}''',
    },
    'typescript': {
        'empty_catch': '''// Before
catch (error) {{}}

// After
catch (error) {{
  logger.error('Operation failed', {{ error: error instanceof Error ? error.message : error }});
  throw new CustomError('Operation failed', {{ cause: error }});
}}''',
    },
    'python': {
        'bare_except_pass': '''# Before
except:
    pass

# After - Specific exception with logging
except SpecificException as e:
    logger.error(f"Operation failed: {{e}}")
    raise  # Re-raise if needed''',
        'exception_pass': '''# Before
except Exception as e:
    pass

# After
except Exception as e:
    logger.exception("Operation failed")
    raise CustomError("Operation failed") from e''',
    },
    'java': {
        'empty_catch': '''// Before
catch (Exception e) {{
}}

// After
catch (Exception e) {{
    logger.error("Operation failed", e);
    throw new RuntimeException("Operation failed", e);
}}''',
    },
    'go': {
        'ignored_error': '''// Before
result, _ := doSomething()

// After
result, err := doSomething()
if err != nil {{
    return fmt.Errorf("operation failed: %w", err)
}}''',
        'empty_error_check': '''// Before
if err != nil {{
}}

// After
if err != nil {{
    return fmt.Errorf("operation failed: %w", err)
}}''',
    },
    'csharp': {
        'empty_catch': '''// Before
catch (Exception) {{
}}

// After
catch (Exception ex) {{
    _logger.LogError(ex, "Operation failed");
    throw;
}}''',
    },
}

# Import finding logic from find_empty_catches
LANGUAGES = {'.js': 'javascript', '.jsx': 'javascript', '.ts': 'typescript', '.tsx': 'typescript', '.py': 'python', '.java': 'java', '.go': 'go', '.cs': 'csharp'}
PATTERNS = {
    'javascript': [(r'catch\s*\([^)]*\)\s*\{\s*\}', 'empty_catch'), (r'catch\s*\([^)]*\)\s*\{\s*return\s*(?:null|undefined|false)?\s*;?\s*\}', 'silent_return')],
    'typescript': [(r'catch\s*\([^)]*\)\s*\{\s*\}', 'empty_catch')],
    'python': [(r'except\s*:\s*pass', 'bare_except_pass'), (r'except\s+\w+(?:\s+as\s+\w+)?:\s*pass', 'exception_pass')],
    'java': [(r'catch\s*\([^)]+\)\s*\{\s*\}', 'empty_catch')],
    'go': [(r',\s*_\s*:?=\s*\w+\([^)]*\)', 'ignored_error'), (r'if\s+err\s*!=\s*nil\s*\{\s*\}', 'empty_error_check')],
    'csharp': [(r'catch\s*(?:\([^)]*\))?\s*\{\s*\}', 'empty_catch')],
}
SKIP_DIRS = {'node_modules', 'vendor', 'venv', '.git', 'dist', 'build'}


def parse_args():
    parser = argparse.ArgumentParser(description='Generate fix suggestions')
    parser.add_argument('directory', nargs='?', default='.')
    parser.add_argument('--output', default='empty_catch_fixes.md')
    return parser.parse_args()


def find_issues(directory):
    """Simplified issue finder."""
    findings = []
    root = Path(directory).resolve()
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            lang = LANGUAGES.get(file_path.suffix.lower())
            if not lang or lang not in PATTERNS:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='replace')
            except:
                continue
            
            for pattern, ptype in PATTERNS[lang]:
                for match in re.finditer(pattern, content):
                    line = content[:match.start()].count('\n') + 1
                    findings.append({
                        'file': str(file_path.relative_to(root)),
                        'line': line,
                        'type': ptype,
                        'language': lang,
                        'content': match.group(0)[:80],
                    })
    
    return findings


def generate_report(findings, directory):
    """Generate markdown fix report."""
    lines = []
    lines.append("# Empty Catch Block Fixes\n")
    lines.append(f"**Scanned:** {directory}")
    lines.append(f"**Issues found:** {len(findings)}\n")
    
    if not findings:
        lines.append("No empty catch blocks found!")
        return '\n'.join(lines)
    
    # Group by language
    by_lang = {}
    for f in findings:
        lang = f['language']
        if lang not in by_lang:
            by_lang[lang] = []
        by_lang[lang].append(f)
    
    for lang, items in by_lang.items():
        lines.append(f"\n## {lang.title()} ({len(items)} issues)\n")
        
        for f in items:
            lines.append(f"### {f['file']}:{f['line']}\n")
            lines.append(f"**Found:** `{f['content']}`\n")
            
            # Get fix template
            fix = FIX_TEMPLATES.get(lang, {}).get(f['type'], 'Add proper error handling.')
            lines.append("**Suggested fix:**\n")
            lines.append(f"```{lang}")
            lines.append(fix)
            lines.append("```\n")
    
    # Summary
    lines.append("\n## Next Steps\n")
    lines.append("1. Review each issue and apply appropriate fix")
    lines.append("2. Add linting rules to prevent new issues:")
    lines.append("   - ESLint: `no-empty` rule")
    lines.append("   - Python: `E722` (bare except)")
    lines.append("3. Consider adding structured logging (Winston, Pino, etc.)")
    
    return '\n'.join(lines)


def main():
    args = parse_args()
    
    print(f"Scanning {args.directory}...", file=sys.stderr)
    findings = find_issues(args.directory)
    
    report = generate_report(findings, args.directory)
    
    output_path = Path(args.output)
    output_path.write_text(report, encoding='utf-8')
    
    print(f"Report written to {output_path}", file=sys.stderr)
    print(f"Found {len(findings)} issues", file=sys.stderr)


if __name__ == '__main__':
    main()
