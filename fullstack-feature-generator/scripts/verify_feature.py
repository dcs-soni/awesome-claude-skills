#!/usr/bin/env python3
"""
Verify generated feature code compiles and follows conventions.

Usage:
    python verify_feature.py <path> --feature <feature-name>

Checks:
    - All files exist
    - TypeScript compiles
    - Tests pass
    - Lint passes
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


def to_kebab_case(text: str) -> str:
    """Convert to kebab-case."""
    import re
    words = re.split(r'[\s_-]+', text.lower())
    return '-'.join(words)


def pluralize(word: str) -> str:
    """Simple pluralization."""
    if word.endswith('y'):
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    return word + 's'


def check_files_exist(root: Path, feature: str) -> List[Tuple[str, bool]]:
    """Check if all expected files exist."""
    kebab = to_kebab_case(feature)
    
    expected_files = [
        f"src/schemas/{kebab}.schema.ts",
        f"src/services/{kebab}.service.ts",
        f"src/controllers/{kebab}.controller.ts",
        f"src/routes/{kebab}.routes.ts",
        f"tests/{kebab}.test.ts",
    ]
    
    results = []
    for filepath in expected_files:
        exists = (root / filepath).exists()
        results.append((filepath, exists))
    
    return results


def run_typecheck(root: Path) -> Tuple[bool, str]:
    """Run TypeScript type checking."""
    try:
        result = subprocess.run(
            ["npm", "run", "typecheck"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "npm not found"
    except subprocess.TimeoutExpired:
        return False, "Typecheck timed out"
    except Exception as e:
        return False, str(e)


def run_tests(root: Path, feature: str) -> Tuple[bool, str]:
    """Run tests for the feature."""
    kebab = to_kebab_case(feature)
    
    try:
        result = subprocess.run(
            ["npm", "test", "--", "--grep", feature],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "npm not found"
    except subprocess.TimeoutExpired:
        return False, "Tests timed out"
    except Exception as e:
        return False, str(e)


def run_lint(root: Path) -> Tuple[bool, str]:
    """Run linting."""
    try:
        result = subprocess.run(
            ["npm", "run", "lint"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "npm not found"
    except subprocess.TimeoutExpired:
        return False, "Lint timed out"
    except Exception as e:
        return False, str(e)


def format_results(feature: str, results: Dict) -> str:
    """Format verification results."""
    lines = []
    
    lines.append("=" * 60)
    lines.append(f"VERIFICATION: {feature}")
    lines.append("=" * 60)
    
    # File checks
    lines.append("\n📁 File Existence:")
    for filepath, exists in results["files"]:
        status = "✅" if exists else "❌"
        lines.append(f"   {status} {filepath}")
    
    # Type check
    lines.append(f"\n🔷 TypeScript:")
    tc_status = "✅ Passed" if results["typecheck"][0] else "❌ Failed"
    lines.append(f"   {tc_status}")
    if not results["typecheck"][0]:
        lines.append(f"   {results['typecheck'][1][:200]}")
    
    # Tests
    lines.append(f"\n🧪 Tests:")
    test_status = "✅ Passed" if results["tests"][0] else "❌ Failed"
    lines.append(f"   {test_status}")
    
    # Lint
    lines.append(f"\n📝 Lint:")
    lint_status = "✅ Passed" if results["lint"][0] else "❌ Failed"
    lines.append(f"   {lint_status}")
    
    # Summary
    all_passed = (
        all(exists for _, exists in results["files"]) and
        results["typecheck"][0] and
        results["tests"][0] and
        results["lint"][0]
    )
    
    lines.append("\n" + "=" * 60)
    if all_passed:
        lines.append("✅ ALL CHECKS PASSED - Feature is ready!")
    else:
        lines.append("❌ SOME CHECKS FAILED - Review and fix issues")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_feature.py <path> --feature <feature-name>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    feature = "example"
    if "--feature" in sys.argv:
        idx = sys.argv.index("--feature")
        if idx + 1 < len(sys.argv):
            feature = sys.argv[idx + 1]
    
    # Run checks
    results = {
        "files": check_files_exist(root, feature),
        "typecheck": (True, "Skipped") if "--skip-typecheck" in sys.argv else run_typecheck(root),
        "tests": (True, "Skipped") if "--skip-tests" in sys.argv else run_tests(root, feature),
        "lint": (True, "Skipped") if "--skip-lint" in sys.argv else run_lint(root),
    }
    
    if "--json" in sys.argv:
        # Convert tuples to lists for JSON
        json_results = {
            "files": [[f, e] for f, e in results["files"]],
            "typecheck": list(results["typecheck"]),
            "tests": list(results["tests"]),
            "lint": list(results["lint"]),
        }
        print(json.dumps(json_results, indent=2))
    else:
        print(format_results(feature, results))


if __name__ == "__main__":
    main()
