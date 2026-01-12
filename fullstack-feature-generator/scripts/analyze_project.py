#!/usr/bin/env python3
"""
Analyze project to detect frameworks, patterns, and conventions.

Usage:
    python analyze_project.py <path>

Output:
    - Detected frameworks (API, ORM, UI)
    - Naming conventions
    - Project structure pattern
    - Existing features to follow
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


def detect_package_manager(root: Path) -> Optional[str]:
    """Detect which package manager is used."""
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    elif (root / "yarn.lock").exists():
        return "yarn"
    elif (root / "package-lock.json").exists():
        return "npm"
    elif (root / "bun.lockb").exists():
        return "bun"
    elif (root / "requirements.txt").exists():
        return "pip"
    elif (root / "Pipfile.lock").exists():
        return "pipenv"
    elif (root / "poetry.lock").exists():
        return "poetry"
    elif (root / "go.mod").exists():
        return "go"
    return None


def detect_frameworks(root: Path) -> Dict[str, str]:
    """Detect API, ORM, and UI frameworks."""
    frameworks = {
        "api": None,
        "orm": None,
        "ui": None,
        "test": None,
        "validation": None,
    }
    
    # Node.js detection
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            # API frameworks
            if "express" in deps:
                frameworks["api"] = "express"
            elif "fastify" in deps:
                frameworks["api"] = "fastify"
            elif "@nestjs/core" in deps:
                frameworks["api"] = "nestjs"
            elif "hono" in deps:
                frameworks["api"] = "hono"
            elif "next" in deps:
                frameworks["api"] = "nextjs"
            
            # ORM
            if "@prisma/client" in deps:
                frameworks["orm"] = "prisma"
            elif "drizzle-orm" in deps:
                frameworks["orm"] = "drizzle"
            elif "typeorm" in deps:
                frameworks["orm"] = "typeorm"
            elif "sequelize" in deps:
                frameworks["orm"] = "sequelize"
            elif "mongoose" in deps:
                frameworks["orm"] = "mongoose"
            
            # UI
            if "next" in deps:
                frameworks["ui"] = "nextjs"
            elif "react" in deps:
                frameworks["ui"] = "react"
            elif "vue" in deps:
                frameworks["ui"] = "vue"
            elif "svelte" in deps:
                frameworks["ui"] = "svelte"
            
            # Test
            if "vitest" in deps:
                frameworks["test"] = "vitest"
            elif "jest" in deps:
                frameworks["test"] = "jest"
            
            # Validation
            if "zod" in deps:
                frameworks["validation"] = "zod"
            elif "yup" in deps:
                frameworks["validation"] = "yup"
            elif "joi" in deps:
                frameworks["validation"] = "joi"
                
        except Exception:
            pass
    
    # Python detection
    req_path = root / "requirements.txt"
    pyproject = root / "pyproject.toml"
    
    if req_path.exists() or pyproject.exists():
        content = ""
        if req_path.exists():
            content = req_path.read_text().lower()
        if pyproject.exists():
            content += pyproject.read_text().lower()
        
        if "fastapi" in content:
            frameworks["api"] = "fastapi"
        elif "flask" in content:
            frameworks["api"] = "flask"
        elif "django" in content:
            frameworks["api"] = "django"
        
        if "sqlalchemy" in content:
            frameworks["orm"] = "sqlalchemy"
        elif "tortoise" in content:
            frameworks["orm"] = "tortoise"
        
        if "pytest" in content:
            frameworks["test"] = "pytest"
        
        if "pydantic" in content:
            frameworks["validation"] = "pydantic"
    
    return {k: v for k, v in frameworks.items() if v}


def detect_architecture(root: Path) -> str:
    """Detect architecture pattern."""
    dirs = set()
    for item in root.iterdir():
        if item.is_dir() and item.name not in IGNORE_DIRS:
            dirs.add(item.name.lower())
    
    src_dirs = set()
    src_path = root / "src"
    if src_path.exists():
        for item in src_path.iterdir():
            if item.is_dir():
                src_dirs.add(item.name.lower())
    
    all_dirs = dirs | src_dirs
    
    if {"domain", "application", "infrastructure"} & all_dirs:
        return "clean-architecture"
    elif {"models", "views", "controllers"} & all_dirs:
        return "mvc"
    elif "features" in all_dirs or "modules" in all_dirs:
        return "feature-based"
    elif "src" in dirs:
        return "standard"
    else:
        return "flat"


def detect_naming_convention(root: Path) -> Dict[str, str]:
    """Detect naming conventions from existing files."""
    conventions = {
        "files": "unknown",
        "functions": "unknown",
        "variables": "unknown",
    }
    
    # Sample some TypeScript/JavaScript files
    for ext in ["*.ts", "*.js"]:
        files = list((root / "src").glob(f"**/{ext}"))[:5] if (root / "src").exists() else []
        
        for f in files:
            name = f.stem
            if "-" in name:
                conventions["files"] = "kebab-case"
            elif "_" in name:
                conventions["files"] = "snake_case"
            elif name[0].isupper():
                conventions["files"] = "PascalCase"
            else:
                conventions["files"] = "camelCase"
            break
    
    return conventions


def find_example_features(root: Path) -> List[Dict]:
    """Find existing features to use as examples."""
    examples = []
    
    # Look for route/controller files
    for pattern in ["**/routes/*.ts", "**/controllers/*.ts", "**/routes/*.py"]:
        for f in root.glob(pattern):
            if any(ignore in str(f) for ignore in IGNORE_DIRS):
                continue
            
            name = f.stem.replace(".routes", "").replace(".controller", "").replace("_routes", "")
            if name not in ["index", "__init__"]:
                examples.append({
                    "name": name,
                    "type": "api",
                    "path": str(f.relative_to(root))
                })
    
    # Look for model files
    for pattern in ["**/models/*.ts", "**/schema/*.ts", "**/models/*.py"]:
        for f in root.glob(pattern):
            if any(ignore in str(f) for ignore in IGNORE_DIRS):
                continue
            
            name = f.stem
            if name not in ["index", "__init__", "base"]:
                examples.append({
                    "name": name,
                    "type": "model",
                    "path": str(f.relative_to(root))
                })
    
    return examples[:10]


def get_project_structure(root: Path) -> Dict:
    """Get recommended locations for new features."""
    structure = {
        "models": None,
        "routes": None,
        "controllers": None,
        "services": None,
        "schemas": None,
        "tests": None,
        "components": None,
    }
    
    search_paths = [
        ("models", ["src/models", "src/db/schema", "models", "prisma"]),
        ("routes", ["src/routes", "src/api", "routes", "app/api"]),
        ("controllers", ["src/controllers", "controllers"]),
        ("services", ["src/services", "services", "src/lib"]),
        ("schemas", ["src/schemas", "schemas", "src/validators"]),
        ("tests", ["tests", "__tests__", "test", "src/__tests__"]),
        ("components", ["src/components", "components", "src/features"]),
    ]
    
    for key, paths in search_paths:
        for path in paths:
            if (root / path).exists():
                structure[key] = path
                break
    
    return {k: v for k, v in structure.items() if v}


def format_output(result: Dict) -> str:
    """Format as readable text."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("PROJECT ANALYSIS FOR FEATURE GENERATION")
    lines.append("=" * 60)
    
    lines.append(f"\n📦 Package Manager: {result.get('package_manager', 'unknown')}")
    
    if result.get("frameworks"):
        lines.append(f"\n🔧 Detected Frameworks:")
        for key, value in result["frameworks"].items():
            lines.append(f"   • {key}: {value}")
    
    lines.append(f"\n🏗️  Architecture: {result.get('architecture', 'unknown')}")
    
    if result.get("conventions"):
        lines.append(f"\n📝 Naming Conventions:")
        for key, value in result["conventions"].items():
            lines.append(f"   • {key}: {value}")
    
    if result.get("structure"):
        lines.append(f"\n📁 Feature Locations:")
        for key, value in result["structure"].items():
            lines.append(f"   • {key}: {value}/")
    
    if result.get("examples"):
        lines.append(f"\n📋 Existing Features (use as reference):")
        for ex in result["examples"][:5]:
            lines.append(f"   • {ex['name']} ({ex['type']}): {ex['path']}")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_project.py <path>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    if not root.exists() or not root.is_dir():
        print(f"Error: '{root}' is not a valid directory")
        sys.exit(1)
    
    result = {
        "package_manager": detect_package_manager(root),
        "frameworks": detect_frameworks(root),
        "architecture": detect_architecture(root),
        "conventions": detect_naming_convention(root),
        "structure": get_project_structure(root),
        "examples": find_example_features(root),
    }
    
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
