#!/usr/bin/env python3
"""
Analyze the structure of a codebase and identify its type, organization, and key files.

Usage:
    python analyze_structure.py <path>

Output:
    - Project type (Node.js, Python, Go, etc.)
    - Directory structure with descriptions
    - Key configuration files found
    - Detected frameworks and libraries
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Files that indicate project type
PROJECT_INDICATORS = {
    "nodejs": ["package.json"],
    "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
    "go": ["go.mod"],
    "rust": ["Cargo.toml"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "dotnet": ["*.csproj", "*.sln"],
    "ruby": ["Gemfile"],
    "php": ["composer.json"],
}

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    "express": {"file": "package.json", "contains": '"express"'},
    "fastify": {"file": "package.json", "contains": '"fastify"'},
    "nestjs": {"file": "package.json", "contains": '"@nestjs/core"'},
    "nextjs": {"file": "package.json", "contains": '"next"'},
    "react": {"file": "package.json", "contains": '"react"'},
    "vue": {"file": "package.json", "contains": '"vue"'},
    "angular": {"file": "package.json", "contains": '"@angular/core"'},
    "django": {"file": "requirements.txt", "contains": "django"},
    "flask": {"file": "requirements.txt", "contains": "flask"},
    "fastapi": {"file": "requirements.txt", "contains": "fastapi"},
    "gin": {"file": "go.mod", "contains": "github.com/gin-gonic/gin"},
    "echo": {"file": "go.mod", "contains": "github.com/labstack/echo"},
}

# Directory descriptions
COMMON_DIRECTORIES = {
    "src": "Source code",
    "lib": "Library code",
    "app": "Application code",
    "components": "UI components",
    "pages": "Page components/routes",
    "routes": "Route definitions",
    "api": "API routes/handlers",
    "controllers": "Request handlers (MVC)",
    "models": "Data models",
    "views": "View templates",
    "services": "Business logic",
    "utils": "Utility functions",
    "helpers": "Helper functions",
    "hooks": "Custom hooks (React)",
    "types": "Type definitions",
    "interfaces": "Interface definitions",
    "config": "Configuration files",
    "constants": "Constant values",
    "assets": "Static assets",
    "public": "Public/static files",
    "static": "Static files",
    "templates": "Template files",
    "tests": "Test files",
    "__tests__": "Test files (Jest)",
    "test": "Test files",
    "spec": "Test specifications",
    "migrations": "Database migrations",
    "prisma": "Prisma ORM files",
    "drizzle": "Drizzle ORM files",
    "db": "Database related",
    "database": "Database related",
    "scripts": "Utility scripts",
    "bin": "Binary/executable scripts",
    "cmd": "Command entry points (Go)",
    "internal": "Internal packages (Go)",
    "pkg": "Public packages (Go)",
    "docs": "Documentation",
    ".github": "GitHub configuration",
    ".vscode": "VS Code settings",
}

# Ignore these directories
IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", ".nuxt", 
    "dist", "build", "out", ".cache", "coverage", "vendor",
    ".idea", ".venv", "venv", "env", ".tox"
}


def detect_project_type(root: Path) -> Tuple[str, List[str]]:
    """Detect the project type based on indicator files."""
    detected_types = []
    indicator_files = []
    
    for project_type, indicators in PROJECT_INDICATORS.items():
        for indicator in indicators:
            if "*" in indicator:
                # Glob pattern
                matches = list(root.glob(indicator))
                if matches:
                    detected_types.append(project_type)
                    indicator_files.extend([m.name for m in matches])
            elif (root / indicator).exists():
                detected_types.append(project_type)
                indicator_files.append(indicator)
    
    primary_type = detected_types[0] if detected_types else "unknown"
    return primary_type, list(set(indicator_files))


def detect_frameworks(root: Path) -> List[str]:
    """Detect frameworks used in the project."""
    frameworks = []
    
    for framework, pattern in FRAMEWORK_PATTERNS.items():
        file_path = root / pattern["file"]
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8").lower()
                if pattern["contains"].lower() in content:
                    frameworks.append(framework)
            except Exception:
                pass
    
    return frameworks


def analyze_directory(root: Path, max_depth: int = 3, current_depth: int = 0) -> Dict:
    """Recursively analyze directory structure."""
    if current_depth > max_depth:
        return {"truncated": True}
    
    result = {
        "name": root.name,
        "type": "directory",
        "children": [],
        "description": COMMON_DIRECTORIES.get(root.name.lower(), "")
    }
    
    try:
        items = sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        
        for item in items:
            if item.name in IGNORE_DIRS or item.name.startswith("."):
                continue
            
            if item.is_dir():
                child = analyze_directory(item, max_depth, current_depth + 1)
                result["children"].append(child)
            elif current_depth <= 1:  # Only show root-level files
                result["children"].append({
                    "name": item.name,
                    "type": "file",
                    "size": item.stat().st_size
                })
    except PermissionError:
        result["error"] = "Permission denied"
    
    return result


def find_key_files(root: Path) -> List[Dict]:
    """Find important configuration and entry point files."""
    key_files = []
    
    important_files = [
        "package.json", "tsconfig.json", "vite.config.ts", "vite.config.js",
        "next.config.js", "next.config.mjs", "webpack.config.js",
        "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
        "go.mod", "go.sum", "Cargo.toml",
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        ".env.example", ".env.sample",
        "README.md", "README.rst", "README.txt",
        "CONTRIBUTING.md", "CHANGELOG.md",
        "Makefile", "justfile",
        ".gitignore", ".dockerignore",
        "eslint.config.js", ".eslintrc.js", ".eslintrc.json",
        "prettier.config.js", ".prettierrc",
        "jest.config.js", "jest.config.ts", "vitest.config.ts",
    ]
    
    for filename in important_files:
        file_path = root / filename
        if file_path.exists():
            key_files.append({
                "name": filename,
                "path": str(file_path.relative_to(root)),
                "size": file_path.stat().st_size
            })
    
    return key_files


def get_stats(root: Path) -> Dict:
    """Get file statistics for the project."""
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "file_types": {}
    }
    
    for item in root.rglob("*"):
        if any(ignore in str(item) for ignore in IGNORE_DIRS):
            continue
        
        if item.is_file():
            stats["total_files"] += 1
            ext = item.suffix.lower() or "no extension"
            stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
        elif item.is_dir():
            stats["total_dirs"] += 1
    
    # Sort file types by count
    stats["file_types"] = dict(
        sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True)[:10]
    )
    
    return stats


def format_output(result: Dict) -> str:
    """Format the analysis result as readable text."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("CODEBASE STRUCTURE ANALYSIS")
    lines.append("=" * 60)
    
    # Project type
    lines.append(f"\n📦 Project Type: {result['project_type'].upper()}")
    if result["indicator_files"]:
        lines.append(f"   Detected via: {', '.join(result['indicator_files'])}")
    
    # Frameworks
    if result["frameworks"]:
        lines.append(f"\n🔧 Frameworks: {', '.join(result['frameworks'])}")
    
    # Stats
    stats = result["stats"]
    lines.append(f"\n📊 Statistics:")
    lines.append(f"   Files: {stats['total_files']}")
    lines.append(f"   Directories: {stats['total_dirs']}")
    
    if stats["file_types"]:
        lines.append(f"\n📄 Top File Types:")
        for ext, count in list(stats["file_types"].items())[:5]:
            lines.append(f"   {ext}: {count}")
    
    # Key files
    if result["key_files"]:
        lines.append(f"\n🔑 Key Files Found:")
        for f in result["key_files"][:15]:
            lines.append(f"   • {f['name']}")
    
    # Directory structure
    lines.append(f"\n📁 Directory Structure:")
    lines.append(format_tree(result["structure"]))
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def format_tree(node: Dict, prefix: str = "", is_last: bool = True) -> str:
    """Format directory tree as text."""
    lines = []
    
    connector = "└── " if is_last else "├── "
    
    if node.get("type") == "directory":
        desc = f" ({node['description']})" if node.get("description") else ""
        lines.append(f"{prefix}{connector}📁 {node['name']}{desc}")
        
        children = node.get("children", [])
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1)
            extension = "    " if is_last else "│   "
            lines.append(format_tree(child, prefix + extension, is_child_last))
    else:
        lines.append(f"{prefix}{connector}📄 {node['name']}")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_structure.py <path>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    if not root.exists():
        print(f"Error: Path '{root}' does not exist")
        sys.exit(1)
    
    if not root.is_dir():
        print(f"Error: Path '{root}' is not a directory")
        sys.exit(1)
    
    # Perform analysis
    project_type, indicator_files = detect_project_type(root)
    frameworks = detect_frameworks(root)
    structure = analyze_directory(root)
    key_files = find_key_files(root)
    stats = get_stats(root)
    
    result = {
        "root": str(root),
        "project_type": project_type,
        "indicator_files": indicator_files,
        "frameworks": frameworks,
        "structure": structure,
        "key_files": key_files,
        "stats": stats
    }
    
    # Output
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
