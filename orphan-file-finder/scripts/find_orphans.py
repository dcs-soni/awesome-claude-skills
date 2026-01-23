#!/usr/bin/env python3
"""
Orphan File Finder

Builds a dependency graph to find source files with zero inbound imports.
Usage: python find_orphans.py <directory> [--format json|text]
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# --- Configuration ---

# Extensions to scan
EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',  # JS/TS
    '.py',  # Python
    '.go',  # Go
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', 'vendor', 'venv', '.venv', '__pycache__', '.git',
    'dist', 'build', '.next', 'target', 'bin', 'obj', '.idea', '.vscode',
    'coverage', 'test', 'tests'
}

# Entry point patterns (whitelist)
ENTRY_POINT_PATTERNS = [
    r'^index\.(js|ts|jsx|tsx)$',
    r'^main\.(js|ts|py|go)$',
    r'^server\.(js|ts)$',
    r'^app\.(js|ts)$',
    r'^cli\.(js|ts|py)$',
    r'^setup\.py$',
    r'^manage\.py$',
    r'^vite\.config\.',
    r'^webpack\.config\.',
    r'^jest\.config\.',
    r'^tsconfig\.json$',
    r'^package\.json$',
    r'^go\.mod$',
    r'^requirements\.txt$',
]

# Regex for imports
REGEX_JS_IMPORT = re.compile(r'(?:^|;|})\s*(?:import\s+(?:[^"\']*\s+from\s+)?|export\s+(?:[^"\']*\s+from\s+)?|require\s*\(\s*)["\']([^"\']+)["\']')
REGEX_PY_IMPORT = re.compile(r'^\s*(?:import\s+([\w\.]+)|from\s+([\w\.]+)\s+import)')
REGEX_GO_IMPORT = re.compile(r'^\s*import\s+(?:\(\s*)?["\']([^"\']+)["\']') # Simplistic Go import

# --- Logic ---

def parse_args():
    parser = argparse.ArgumentParser(description='Find orphan source files')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan')
    parser.add_argument('--format', choices=['json', 'text'], default='text')
    parser.add_argument('--ignore', default='', help='Comma-separated patterns to ignore')
    return parser.parse_args()

def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if pattern and path.match(pattern):
            return True
    return False

def get_entry_points(files):
    """Identify likely entry points based on filenames."""
    entry_points = set()
    for f in files:
        name = Path(f).name
        for pattern in ENTRY_POINT_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                entry_points.add(f)
                break
    return entry_points

def resolve_import(base_file, import_path, all_files_map):
    """
    Resolve partial import paths to absolute file paths.
    
    Args:
        base_file: Path object of the file containing the import
        import_path: String of the imported path (e.g., './utils', 'react')
        all_files_map: Dict mapping filename (no ext) to full Path list
    """
    # 1. External dependencies / packages (simple heuristic: no ./ or ../)
    if not import_path.startswith('.'):
        # Python: 'utils.helper' -> 'utils/helper.py'
        # JS: 'react' -> node_modules (ignored)
        # Check if it maps to a local file (Python module style)
        py_path = import_path.replace('.', '/')
        
        # Check exact matches in our file map (heuristic for Python absolute imports)
        candidates = all_files_map.get(Path(py_path).name, [])
        for c in candidates:
            # Very wide net: if simple name matches, assume linked for now to be safe
            if str(c).endswith(py_path + '.py'):
                return str(c)
        return None

    # 2. Relative imports
    try:
        # Resolve relative to base_file dir
        target = (base_file.parent / import_path).resolve()
    except ValueError:
        return None

    # Exact file match?
    if str(target) in all_files_map.get('__FULL_PATHS__', set()):
        return str(target)

    # Try extensions
    for ext in EXTENSIONS:
        candidate = target.with_suffix(ext)
        if str(candidate) in all_files_map.get('__FULL_PATHS__', set()):
            return str(candidate)
        
    # Try index files (JS/TS mostly)
    for ext in EXTENSIONS:
        candidate = target / f"index{ext}"
        if str(candidate) in all_files_map.get('__FULL_PATHS__', set()):
            return str(candidate)

    return None

def scan_imports(file_path):
    """Extract imported paths from a file."""
    imports = set()
    ext = file_path.suffix.lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            if ext in {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}:
                for match in REGEX_JS_IMPORT.finditer(content):
                    imports.add(match.group(1))
            
            elif ext == '.py':
                for line in content.splitlines():
                    match = REGEX_PY_IMPORT.match(line)
                    if match:
                        # group 1 is 'import X', group 2 is 'from X import'
                        imports.add(match.group(1) or match.group(2))
            
            elif ext == '.go':
                # Go parsing is complex with multiline imports, simplistic regex for single line
                # or straightforward blocks. Better use `go list` but keeping stdlib only here.
                pass 

    except Exception:
        pass
        
    return imports

def main():
    args = parse_args()
    root = Path(args.directory).resolve()
    ignore_patterns = args.ignore.split(',') if args.ignore else []

    # 1. Index all files
    all_files = []
    # Map filename -> [full_paths] for fuzzy matching
    file_map = defaultdict(list)
    full_path_set = set()

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden/ignored dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        
        for f in filenames:
            path = Path(dirpath) / f
            if path.suffix.lower() in EXTENSIONS:
                # Check ignores
                rel_path = path.relative_to(root)
                if is_ignored(rel_path, ignore_patterns):
                    continue
                    
                full_str = str(path)
                all_files.append(full_str)
                file_map[path.name].append(path)
                file_map[path.stem].append(path) # stem for python modules
                full_path_set.add(full_str)

    # Add special key for O(1) existence check
    file_map['__FULL_PATHS__'] = full_path_set

    # 2. Build Graph (Adjacency List & In-Degree)
    in_degree = {f: 0 for f in all_files}
    graph = defaultdict(set)

    print(f"Scanning {len(all_files)} files...", file=sys.stderr)

    for f in all_files:
        path_obj = Path(f)
        raw_imports = scan_imports(path_obj)
        
        for imp in raw_imports:
            resolved = resolve_import(path_obj, imp, file_map)
            if resolved and resolved in in_degree:
                if resolved != f: # Self-import doesn't count
                    graph[f].add(resolved)
                    # We only increment if we haven't counted this edge yet? 
                    # Actually graph is a set of outgoing edges.
                    # Use logic: A imports B. B in-degree++
                    pass

    # Re-calculate in-degree correctly from graph
    # graph keys are consumers, values are dependencies
    # Wait, my logic above in loop was slightly off for graph-building vs in-degree.
    # Correct approach:
    # For every file, find what it imports. For each import 'target': in_degree[target] += 1
    
    # Reset in-degree to be safe and recalculate
    in_degree = {f: 0 for f in all_files}
    
    for consumer in all_files:
        path_obj = Path(consumer)
        raw_imports = scan_imports(path_obj)
        for imp in raw_imports:
            resolved = resolve_import(path_obj, imp, file_map)
            if resolved and resolved in in_degree:
                if resolved != consumer:
                    in_degree[resolved] += 1

    # 3. Identify Orphans
    orphans = []
    entry_points = get_entry_points(all_files)
    
    for f, degree in in_degree.items():
        if degree == 0:
            orphans.append(f)

    # Filter entry points
    true_orphans = [f for f in orphans if f not in entry_points]
    likely_entry_points = [f for f in orphans if f in entry_points]

    # 4. Output
    processed_orphans = [str(Path(f).relative_to(root)) for f in true_orphans]
    processed_entry = [str(Path(f).relative_to(root)) for f in likely_entry_points]

    if args.format == 'json':
        print(json.dumps({
            "orphans": processed_orphans,
            "likely_entry_points": processed_entry,
            "count": len(processed_orphans)
        }, indent=2))
    else:
        print(f"Found {len(processed_orphans)} potential orphan files.")
        print("-" * 60)
        
        if processed_entry:
            print("\nLikely Entry Points (Whitelisted):")
            for f in sorted(processed_entry):
                print(f"  [OK] {f}")

        print("\nPotential Orphans (No Inbound References):")
        if not processed_orphans:
            print("  (None found)")
        else:
            for f in sorted(processed_orphans):
                print(f"  [?] {f}")
        
        print("\n" + "-" * 60)
        print("Tip: Verify these files are truly unused before deleting.")

if __name__ == '__main__':
    main()
