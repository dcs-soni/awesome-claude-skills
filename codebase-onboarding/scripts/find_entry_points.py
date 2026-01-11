#!/usr/bin/env python3
"""
Find entry points in a codebase - main files, API routes, CLI commands.

Usage:
    python find_entry_points.py <path>

Output:
    - Main application files
    - API route definitions
    - CLI entry points
    - Event handlers
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", ".nuxt",
    "dist", "build", "out", ".cache", "coverage", "vendor",
    ".idea", ".venv", "venv", "env"
}

ENTRY_PATTERNS = {
    "nodejs": {
        "main_files": [
            "index.js", "index.ts", "main.js", "main.ts",
            "server.js", "server.ts", "app.js", "app.ts",
            "src/index.js", "src/index.ts", "src/main.js", "src/main.ts",
            "src/server.js", "src/server.ts", "src/app.js", "src/app.ts"
        ],
        "patterns": {
            "express_app": r"(app|server)\s*[=:]\s*(express|require\(['\"]express['\"]\))\s*\(\)",
            "fastify_app": r"(app|server)\s*[=:]\s*fastify\s*\(",
            "http_server": r"(http|https)\.createServer\s*\(",
            "listen": r"\.(listen)\s*\(\s*(\d+|process\.env\.\w+)",
            "export_default": r"export\s+default\s+(app|server)",
        }
    },
    "python": {
        "main_files": [
            "main.py", "app.py", "run.py", "server.py",
            "__main__.py", "manage.py", "wsgi.py", "asgi.py"
        ],
        "patterns": {
            "flask_app": r"app\s*=\s*Flask\s*\(",
            "fastapi_app": r"app\s*=\s*FastAPI\s*\(",
            "django_urls": r"urlpatterns\s*=",
            "main_guard": r"if\s+__name__\s*==\s*['\"]__main__['\"]",
            "click_command": r"@click\.(command|group)",
            "argparse": r"argparse\.ArgumentParser\s*\(",
        }
    },
    "go": {
        "main_files": [
            "main.go", "cmd/*/main.go"
        ],
        "patterns": {
            "main_func": r"func\s+main\s*\(\s*\)",
            "http_handle": r"http\.(HandleFunc|Handle)\s*\(",
            "gin_router": r"gin\.(Default|New)\s*\(\)",
            "echo_router": r"echo\.New\s*\(\)",
        }
    }
}

ROUTE_PATTERNS = {
    "express": [
        r"(app|router)\.(get|post|put|patch|delete|all)\s*\(\s*['\"]([^'\"]+)['\"]",
        r"(app|router)\.use\s*\(\s*['\"]([^'\"]+)['\"]",
    ],
    "fastify": [
        r"(app|fastify)\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]",
    ],
    "flask": [
        r"@app\.route\s*\(\s*['\"]([^'\"]+)['\"]",
        r"@blueprint\.route\s*\(\s*['\"]([^'\"]+)['\"]",
    ],
    "fastapi": [
        r"@app\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]",
        r"@router\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]",
    ],
    "django": [
        r"path\s*\(\s*['\"]([^'\"]+)['\"]",
        r"url\s*\(\s*r?['\"]([^'\"]+)['\"]",
    ],
    "nextjs_pages": [
        r"pages/(.+)\.(js|ts|jsx|tsx)$",
    ],
    "nextjs_app": [
        r"app/(.+)/page\.(js|ts|jsx|tsx)$",
        r"app/(.+)/route\.(js|ts|jsx|tsx)$",
    ],
}


def detect_project_type(root: Path) -> str:
    """Detect project type."""
    if (root / "package.json").exists():
        return "nodejs"
    elif (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        return "python"
    elif (root / "go.mod").exists():
        return "go"
    return "unknown"


def find_main_files(root: Path, project_type: str) -> List[Dict]:
    """Find main/entry point files."""
    results = []
    patterns = ENTRY_PATTERNS.get(project_type, {})
    main_files = patterns.get("main_files", [])
    
    for pattern in main_files:
        if "*" in pattern:
            matches = list(root.glob(pattern))
            for match in matches:
                results.append({
                    "path": str(match.relative_to(root)),
                    "type": "main_file",
                    "reason": "matches pattern: " + pattern
                })
        else:
            file_path = root / pattern
            if file_path.exists():
                results.append({
                    "path": pattern,
                    "type": "main_file",
                    "reason": "standard entry point"
                })
    
    # Check package.json for main/bin
    if project_type == "nodejs":
        pkg_path = root / "package.json"
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text())
                if "main" in pkg:
                    results.append({
                        "path": pkg["main"],
                        "type": "package_main",
                        "reason": "package.json main field"
                    })
                if "bin" in pkg:
                    bins = pkg["bin"]
                    if isinstance(bins, str):
                        results.append({
                            "path": bins,
                            "type": "cli_entry",
                            "reason": "package.json bin field"
                        })
                    elif isinstance(bins, dict):
                        for name, path in bins.items():
                            results.append({
                                "path": path,
                                "type": "cli_entry",
                                "name": name,
                                "reason": f"package.json bin: {name}"
                            })
            except Exception:
                pass
    
    return results


def scan_for_patterns(root: Path, project_type: str) -> List[Dict]:
    """Scan files for entry point patterns."""
    results = []
    patterns = ENTRY_PATTERNS.get(project_type, {}).get("patterns", {})
    
    extensions = {
        "nodejs": [".js", ".ts", ".mjs", ".cjs"],
        "python": [".py"],
        "go": [".go"]
    }.get(project_type, [])
    
    for file_path in root.rglob("*"):
        if any(ignore in str(file_path) for ignore in IGNORE_DIRS):
            continue
        
        if file_path.suffix not in extensions:
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    results.append({
                        "path": str(file_path.relative_to(root)),
                        "type": "pattern_match",
                        "pattern": pattern_name,
                        "matches": len(matches) if isinstance(matches[0], str) else len(matches)
                    })
        except Exception:
            pass
    
    return results


def find_routes(root: Path, project_type: str) -> List[Dict]:
    """Find API route definitions."""
    results = []
    
    # Detect framework
    framework = None
    pkg_path = root / "package.json"
    req_path = root / "requirements.txt"
    
    if pkg_path.exists():
        try:
            content = pkg_path.read_text().lower()
            if '"express"' in content:
                framework = "express"
            elif '"fastify"' in content:
                framework = "fastify"
            elif '"next"' in content:
                framework = "nextjs_app" if (root / "app").exists() else "nextjs_pages"
        except Exception:
            pass
    
    if req_path.exists():
        try:
            content = req_path.read_text().lower()
            if "flask" in content:
                framework = "flask"
            elif "fastapi" in content:
                framework = "fastapi"
            elif "django" in content:
                framework = "django"
        except Exception:
            pass
    
    if not framework:
        return results
    
    patterns = ROUTE_PATTERNS.get(framework, [])
    
    # Handle Next.js file-based routing
    if framework.startswith("nextjs"):
        if framework == "nextjs_pages" and (root / "pages").exists():
            for f in (root / "pages").rglob("*.tsx"):
                route = "/" + str(f.relative_to(root / "pages")).replace("\\", "/")
                route = re.sub(r"\.(tsx|ts|jsx|js)$", "", route)
                route = route.replace("/index", "").replace("[", ":").replace("]", "")
                if not route:
                    route = "/"
                results.append({
                    "path": str(f.relative_to(root)),
                    "route": route,
                    "type": "page"
                })
        
        if framework == "nextjs_app" and (root / "app").exists():
            for f in (root / "app").rglob("page.tsx"):
                route = "/" + str(f.parent.relative_to(root / "app")).replace("\\", "/")
                route = route.replace("[", ":").replace("]", "")
                if route == "/.":
                    route = "/"
                results.append({
                    "path": str(f.relative_to(root)),
                    "route": route,
                    "type": "page"
                })
            
            for f in (root / "app").rglob("route.ts"):
                route = "/" + str(f.parent.relative_to(root / "app")).replace("\\", "/")
                route = route.replace("[", ":").replace("]", "")
                if route == "/.":
                    route = "/"
                results.append({
                    "path": str(f.relative_to(root)),
                    "route": route,
                    "type": "api_route"
                })
        
        return results
    
    # Scan files for route patterns
    extensions = [".js", ".ts", ".py"]
    
    for file_path in root.rglob("*"):
        if any(ignore in str(file_path) for ignore in IGNORE_DIRS):
            continue
        
        if file_path.suffix not in extensions:
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        route = match[-1] if len(match) > 1 else match[0]
                    else:
                        route = match
                    
                    results.append({
                        "path": str(file_path.relative_to(root)),
                        "route": route,
                        "type": "route"
                    })
        except Exception:
            pass
    
    return results


def format_output(result: Dict) -> str:
    """Format results as readable text."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("ENTRY POINTS ANALYSIS")
    lines.append("=" * 60)
    
    lines.append(f"\n📦 Project Type: {result['project_type'].upper()}")
    
    # Main files
    if result["main_files"]:
        lines.append(f"\n🚀 Main Entry Points:")
        for entry in result["main_files"]:
            lines.append(f"   • {entry['path']}")
            lines.append(f"     └─ {entry['reason']}")
    
    # Pattern matches
    if result["patterns"]:
        lines.append(f"\n🔍 Pattern Matches:")
        for entry in result["patterns"][:10]:
            lines.append(f"   • {entry['path']}")
            lines.append(f"     └─ {entry['pattern']} ({entry['matches']} matches)")
    
    # Routes
    if result["routes"]:
        lines.append(f"\n🛣️  Routes Found ({len(result['routes'])} total):")
        # Group by file
        routes_by_file = {}
        for route in result["routes"]:
            path = route["path"]
            if path not in routes_by_file:
                routes_by_file[path] = []
            routes_by_file[path].append(route["route"])
        
        for path, routes in list(routes_by_file.items())[:10]:
            lines.append(f"   📄 {path}")
            for route in routes[:5]:
                lines.append(f"      └─ {route}")
            if len(routes) > 5:
                lines.append(f"      └─ ... and {len(routes) - 5} more")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_entry_points.py <path>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    if not root.exists() or not root.is_dir():
        print(f"Error: '{root}' is not a valid directory")
        sys.exit(1)
    
    project_type = detect_project_type(root)
    main_files = find_main_files(root, project_type)
    patterns = scan_for_patterns(root, project_type)
    routes = find_routes(root, project_type)
    
    result = {
        "project_type": project_type,
        "main_files": main_files,
        "patterns": patterns,
        "routes": routes
    }
    
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
