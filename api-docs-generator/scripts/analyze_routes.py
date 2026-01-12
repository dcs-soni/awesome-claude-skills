#!/usr/bin/env python3
"""
Analyze API routes in a codebase and extract endpoint information.

Usage:
    python analyze_routes.py <path>

Output:
    - Detected framework
    - List of all routes with methods, paths, and handlers
    - Middleware detected
    - Validation schemas found
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", ".nuxt",
    "dist", "build", "out", ".cache", "coverage", "vendor",
    ".idea", ".venv", "venv", "env"
}

# Route patterns by framework
ROUTE_PATTERNS = {
    "express": [
        # router.get('/path', handler)
        r"(?:router|app)\.(get|post|put|patch|delete|all)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
        # router.use('/prefix', routerName)
        r"(?:router|app)\.use\s*\(\s*['\"`]([^'\"`]+)['\"`]\s*,\s*(\w+)",
    ],
    "fastify": [
        r"(?:fastify|app)\.(get|post|put|patch|delete)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
    ],
    "hono": [
        r"(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
    ],
    "fastapi": [
        r"@(?:router|app)\.(get|post|put|patch|delete)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
    ],
    "flask": [
        r"@(?:app|blueprint)\.route\s*\(\s*['\"`]([^'\"`]+)['\"`](?:.*?methods\s*=\s*\[([^\]]+)\])?",
    ],
    "django": [
        r"path\s*\(\s*['\"`]([^'\"`]+)['\"`]",
        r"url\s*\(\s*r?['\"`]([^'\"`]+)['\"`]",
    ],
    "gin": [
        r"(?:router|r|group)\.(GET|POST|PUT|PATCH|DELETE)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
    ],
    "echo": [
        r"(?:e|echo|g)\.(GET|POST|PUT|PATCH|DELETE)\s*\(\s*['\"`]([^'\"`]+)['\"`]",
    ],
}

# Middleware patterns
MIDDLEWARE_PATTERNS = {
    "auth": [
        r"auth(?:enticate)?(?:Middleware)?",
        r"requireAuth",
        r"isAuthenticated",
        r"jwt",
        r"passport",
        r"@requires_auth",
        r"Depends\(.*current_user",
    ],
    "validation": [
        r"validate(?:Request)?(?:Body)?",
        r"validateSchema",
        r"@validate",
        r"@Body\(",
    ],
    "rate_limit": [
        r"rateLimit",
        r"RateLimiter",
        r"throttle",
    ],
}


def detect_framework(root: Path) -> Optional[str]:
    """Detect the API framework used."""
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            if "express" in deps:
                return "express"
            elif "fastify" in deps:
                return "fastify"
            elif "@hono/node-server" in deps or "hono" in deps:
                return "hono"
            elif "next" in deps:
                return "nextjs"
            elif "@nestjs/core" in deps:
                return "nestjs"
        except Exception:
            pass
    
    # Python frameworks
    for pyfile in ["requirements.txt", "pyproject.toml"]:
        py_path = root / pyfile
        if py_path.exists():
            try:
                content = py_path.read_text().lower()
                if "fastapi" in content:
                    return "fastapi"
                elif "flask" in content:
                    return "flask"
                elif "django" in content:
                    return "django"
            except Exception:
                pass
    
    # Go frameworks
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            content = go_mod.read_text()
            if "gin-gonic" in content:
                return "gin"
            elif "labstack/echo" in content:
                return "echo"
            elif "go-chi" in content:
                return "chi"
        except Exception:
            pass
    
    return None


def find_route_files(root: Path, framework: str) -> List[Path]:
    """Find files likely to contain route definitions."""
    route_files = []
    
    # Common route directories
    route_dirs = [
        "src/routes", "routes", "src/api", "api",
        "src/controllers", "controllers",
        "app/api", "pages/api",  # Next.js
    ]
    
    # Extensions by framework
    extensions = {
        "express": [".ts", ".js"],
        "fastify": [".ts", ".js"],
        "hono": [".ts", ".js"],
        "nextjs": [".ts", ".tsx", ".js", ".jsx"],
        "nestjs": [".controller.ts"],
        "fastapi": [".py"],
        "flask": [".py"],
        "django": [".py"],
        "gin": [".go"],
        "echo": [".go"],
    }
    
    exts = extensions.get(framework, [".ts", ".js", ".py", ".go"])
    
    # Search in route directories
    for route_dir in route_dirs:
        dir_path = root / route_dir
        if dir_path.exists():
            for ext in exts:
                route_files.extend(dir_path.rglob(f"*{ext}"))
    
    # Also search src root for files with route-related names
    src_path = root / "src"
    if src_path.exists():
        for ext in exts:
            for pattern in ["*route*", "*router*", "*controller*", "*api*"]:
                route_files.extend(src_path.rglob(f"{pattern}{ext}"))
    
    # Filter out ignored dirs
    route_files = [
        f for f in route_files
        if not any(ignore in str(f) for ignore in IGNORE_DIRS)
    ]
    
    return list(set(route_files))


def extract_routes(file_path: Path, framework: str) -> List[Dict]:
    """Extract route definitions from a file."""
    routes = []
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        
        patterns = ROUTE_PATTERNS.get(framework, ROUTE_PATTERNS["express"])
        
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) >= 2:
                            method = match[0].upper()
                            path = match[1]
                        else:
                            method = "GET"
                            path = match[0]
                    else:
                        method = "GET"
                        path = match
                    
                    # Check for middleware in the same line or nearby
                    middleware = detect_middleware(line)
                    
                    routes.append({
                        "method": method,
                        "path": path,
                        "file": str(file_path),
                        "line": i,
                        "middleware": middleware,
                    })
    except Exception as e:
        pass
    
    return routes


def extract_nextjs_routes(root: Path) -> List[Dict]:
    """Extract routes from Next.js App Router or Pages Router."""
    routes = []
    
    # App Router: app/api/**
    app_api = root / "app" / "api"
    if app_api.exists():
        for route_file in app_api.rglob("route.ts"):
            # Convert file path to route path
            relative = route_file.parent.relative_to(app_api)
            path = "/" + str(relative).replace("\\", "/")
            path = re.sub(r'\[([^\]]+)\]', r'{\1}', path)  # [id] -> {id}
            
            # Read file to find methods
            try:
                content = route_file.read_text()
                methods = re.findall(r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)", content)
                for method in methods:
                    routes.append({
                        "method": method,
                        "path": f"/api{path}",
                        "file": str(route_file),
                        "line": 1,
                        "middleware": [],
                    })
            except Exception:
                pass
    
    # Pages Router: pages/api/**
    pages_api = root / "pages" / "api"
    if pages_api.exists():
        for api_file in pages_api.rglob("*.ts"):
            if api_file.name.startswith("_"):
                continue
            
            relative = api_file.relative_to(pages_api)
            path = "/" + str(relative).replace("\\", "/")
            path = path.replace(".ts", "").replace(".js", "")
            path = re.sub(r'\[([^\]]+)\]', r'{\1}', path)
            
            routes.append({
                "method": "GET,POST,PUT,DELETE",
                "path": f"/api{path}",
                "file": str(api_file),
                "line": 1,
                "middleware": [],
            })
    
    return routes


def detect_middleware(line: str) -> List[str]:
    """Detect middleware in a route definition."""
    middleware = []
    
    for mw_type, patterns in MIDDLEWARE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                middleware.append(mw_type)
                break
    
    return middleware


def find_schemas(root: Path, framework: str) -> List[Dict]:
    """Find validation schemas in the codebase."""
    schemas = []
    
    schema_patterns = {
        "zod": r"(?:export\s+)?(?:const|let)\s+(\w+Schema)\s*=\s*z\.object\(",
        "pydantic": r"class\s+(\w+)\s*\(\s*(?:BaseModel|Schema)\s*\)",
        "joi": r"(?:export\s+)?(?:const|let)\s+(\w+Schema)\s*=\s*Joi\.object\(",
    }
    
    search_dirs = ["src/schemas", "schemas", "src/validators", "src/models"]
    
    for search_dir in search_dirs:
        dir_path = root / search_dir
        if dir_path.exists():
            for f in dir_path.rglob("*"):
                if f.suffix in [".ts", ".js", ".py"]:
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        
                        for schema_type, pattern in schema_patterns.items():
                            matches = re.findall(pattern, content)
                            for match in matches:
                                schemas.append({
                                    "name": match,
                                    "type": schema_type,
                                    "file": str(f.relative_to(root)),
                                })
                    except Exception:
                        pass
    
    return schemas


def format_output(result: Dict) -> str:
    """Format results as readable text."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("API ROUTE ANALYSIS")
    lines.append("=" * 60)
    
    lines.append(f"\n🔧 Framework: {result.get('framework', 'unknown').upper()}")
    lines.append(f"📁 Route Files: {len(result.get('files', []))}")
    lines.append(f"🛣️  Total Routes: {len(result.get('routes', []))}")
    
    # Group routes by path prefix
    routes = result.get("routes", [])
    if routes:
        lines.append(f"\n📋 Routes:")
        
        # Sort by path
        sorted_routes = sorted(routes, key=lambda r: r["path"])
        
        for route in sorted_routes[:30]:
            method = route["method"]
            path = route["path"]
            mw = ", ".join(route.get("middleware", [])) or "-"
            lines.append(f"   {method:7} {path:40} [{mw}]")
        
        if len(routes) > 30:
            lines.append(f"   ... and {len(routes) - 30} more routes")
    
    # Schemas
    schemas = result.get("schemas", [])
    if schemas:
        lines.append(f"\n📝 Validation Schemas Found: {len(schemas)}")
        for schema in schemas[:10]:
            lines.append(f"   • {schema['name']} ({schema['type']})")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_routes.py <path>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    if not root.exists() or not root.is_dir():
        print(f"Error: '{root}' is not a valid directory")
        sys.exit(1)
    
    # Detect framework
    framework = detect_framework(root)
    
    # Find and analyze routes
    routes = []
    files = []
    
    if framework == "nextjs":
        routes = extract_nextjs_routes(root)
        files = [r["file"] for r in routes]
    elif framework:
        files = find_route_files(root, framework)
        for f in files:
            routes.extend(extract_routes(f, framework))
    
    # Find schemas
    schemas = find_schemas(root, framework or "express")
    
    result = {
        "framework": framework,
        "files": [str(f) for f in files],
        "routes": routes,
        "schemas": schemas,
    }
    
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
