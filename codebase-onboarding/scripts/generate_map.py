#!/usr/bin/env python3
"""
Generate a comprehensive codebase map and onboarding guide.

Usage:
    python generate_map.py <path> --output ONBOARDING.md

Output:
    - Architecture diagram (Mermaid)
    - Component overview
    - Data flow diagrams
    - Quick reference guide
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", ".nuxt",
    "dist", "build", "out", ".cache", "coverage", "vendor",
    ".idea", ".venv", "venv", "env"
}


def detect_project_info(root: Path) -> Dict:
    """Detect project information."""
    info = {
        "name": root.name,
        "type": "unknown",
        "framework": None,
        "description": "",
    }
    
    # Try package.json
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            info["name"] = pkg.get("name", info["name"])
            info["description"] = pkg.get("description", "")
            info["type"] = "nodejs"
            
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                info["framework"] = "Next.js"
            elif "express" in deps:
                info["framework"] = "Express"
            elif "fastify" in deps:
                info["framework"] = "Fastify"
            elif "@nestjs/core" in deps:
                info["framework"] = "NestJS"
            elif "react" in deps:
                info["framework"] = "React"
            elif "vue" in deps:
                info["framework"] = "Vue"
        except Exception:
            pass
    
    # Try pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        info["type"] = "python"
        try:
            content = pyproject.read_text()
            if "django" in content.lower():
                info["framework"] = "Django"
            elif "fastapi" in content.lower():
                info["framework"] = "FastAPI"
            elif "flask" in content.lower():
                info["framework"] = "Flask"
        except Exception:
            pass
    
    # Try go.mod
    if (root / "go.mod").exists():
        info["type"] = "go"
        try:
            content = (root / "go.mod").read_text()
            if "gin-gonic" in content:
                info["framework"] = "Gin"
            elif "labstack/echo" in content:
                info["framework"] = "Echo"
        except Exception:
            pass
    
    return info


def get_directory_tree(root: Path, max_depth: int = 2) -> List[Dict]:
    """Get directory tree with descriptions."""
    DESCRIPTIONS = {
        "src": "Source code",
        "lib": "Library code",
        "app": "Application (routes/pages)",
        "api": "API routes",
        "pages": "Page components",
        "components": "UI components",
        "hooks": "Custom hooks",
        "utils": "Utility functions",
        "services": "Business logic",
        "models": "Data models",
        "types": "TypeScript types",
        "config": "Configuration",
        "tests": "Test files",
        "__tests__": "Test files",
        "public": "Static assets",
        "assets": "Asset files",
        "styles": "Stylesheets",
        "prisma": "Database schema",
        "migrations": "DB migrations",
        "scripts": "Utility scripts",
        "docs": "Documentation",
    }
    
    tree = []
    
    def walk(path: Path, depth: int):
        if depth > max_depth:
            return
        
        try:
            for item in sorted(path.iterdir()):
                if item.name in IGNORE_DIRS or item.name.startswith("."):
                    continue
                
                if item.is_dir():
                    desc = DESCRIPTIONS.get(item.name.lower(), "")
                    tree.append({
                        "name": item.name,
                        "path": str(item.relative_to(root)),
                        "type": "directory",
                        "description": desc,
                        "depth": depth
                    })
                    walk(item, depth + 1)
        except PermissionError:
            pass
    
    walk(root, 0)
    return tree


def find_key_components(root: Path) -> List[Dict]:
    """Find key components in the codebase."""
    components = []
    
    # Look for common key files
    key_patterns = [
        ("src/index.ts", "Application entry point"),
        ("src/index.js", "Application entry point"),
        ("src/main.ts", "Main entry point"),
        ("src/app.ts", "Application setup"),
        ("app/layout.tsx", "Root layout (Next.js)"),
        ("app/page.tsx", "Home page (Next.js)"),
        ("pages/index.tsx", "Home page (Next.js Pages)"),
        ("pages/_app.tsx", "App wrapper (Next.js Pages)"),
        ("src/routes/index.ts", "Route definitions"),
        ("prisma/schema.prisma", "Database schema"),
        ("drizzle/schema.ts", "Database schema"),
    ]
    
    for pattern, desc in key_patterns:
        path = root / pattern
        if path.exists():
            components.append({
                "path": pattern,
                "description": desc,
                "type": "entry"
            })
    
    # Find models/types
    for model_dir in ["src/models", "src/types", "src/entities", "models"]:
        dir_path = root / model_dir
        if dir_path.exists():
            for f in dir_path.glob("*.ts"):
                if f.name != "index.ts":
                    components.append({
                        "path": str(f.relative_to(root)),
                        "description": f"Data model: {f.stem}",
                        "type": "model"
                    })
    
    # Find services
    for svc_dir in ["src/services", "services", "src/lib"]:
        dir_path = root / svc_dir
        if dir_path.exists():
            for f in dir_path.glob("*.ts"):
                if f.name != "index.ts":
                    components.append({
                        "path": str(f.relative_to(root)),
                        "description": f"Service: {f.stem}",
                        "type": "service"
                    })
    
    return components[:20]  # Limit to 20


def generate_mermaid_diagram(info: Dict, tree: List[Dict]) -> str:
    """Generate a Mermaid architecture diagram."""
    diagram = ["```mermaid", "graph TB"]
    
    # Add project node
    diagram.append(f'    ROOT["{info["name"]}"]')
    
    # Group directories by type
    top_dirs = [d for d in tree if d["depth"] == 0]
    
    for d in top_dirs[:8]:  # Limit to 8 top-level dirs
        safe_name = d["name"].replace("-", "_").replace(".", "_")
        desc = d["description"] or d["name"]
        diagram.append(f'    {safe_name}["{d["name"]}<br/><small>{desc}</small>"]')
        diagram.append(f'    ROOT --> {safe_name}')
    
    diagram.append("```")
    return "\n".join(diagram)


def generate_onboarding_guide(root: Path, output_path: str = None) -> str:
    """Generate the full onboarding guide."""
    info = detect_project_info(root)
    tree = get_directory_tree(root)
    components = find_key_components(root)
    mermaid = generate_mermaid_diagram(info, tree)
    
    lines = []
    
    # Header
    lines.append(f"# {info['name']} - Developer Onboarding Guide")
    lines.append("")
    lines.append(f"> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    if info["description"]:
        lines.append(f"**Description:** {info['description']}")
        lines.append("")
    
    lines.append(f"**Project Type:** {info['type'].upper()}")
    if info["framework"]:
        lines.append(f"**Framework:** {info['framework']}")
    lines.append("")
    
    # Architecture
    lines.append("## Architecture Overview")
    lines.append("")
    lines.append(mermaid)
    lines.append("")
    
    # Directory Structure
    lines.append("## Project Structure")
    lines.append("")
    lines.append("```")
    for d in tree:
        indent = "  " * d["depth"]
        desc = f" # {d['description']}" if d["description"] else ""
        lines.append(f"{indent}{d['name']}/{desc}")
    lines.append("```")
    lines.append("")
    
    # Key Components
    lines.append("## Key Components")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    for comp in components:
        lines.append(f"| `{comp['path']}` | {comp['description']} |")
    lines.append("")
    
    # Getting Started
    lines.append("## Getting Started")
    lines.append("")
    
    if info["type"] == "nodejs":
        lines.append("### Installation")
        lines.append("```bash")
        lines.append("npm install  # or pnpm install / yarn")
        lines.append("```")
        lines.append("")
        lines.append("### Development")
        lines.append("```bash")
        lines.append("npm run dev")
        lines.append("```")
    elif info["type"] == "python":
        lines.append("### Installation")
        lines.append("```bash")
        lines.append("pip install -r requirements.txt")
        lines.append("# or: poetry install / pipenv install")
        lines.append("```")
        lines.append("")
        lines.append("### Development")
        lines.append("```bash")
        lines.append("python main.py  # or: python manage.py runserver")
        lines.append("```")
    elif info["type"] == "go":
        lines.append("### Installation")
        lines.append("```bash")
        lines.append("go mod download")
        lines.append("```")
        lines.append("")
        lines.append("### Development")
        lines.append("```bash")
        lines.append("go run .")
        lines.append("```")
    lines.append("")
    
    # Quick Reference
    lines.append("## Quick Reference")
    lines.append("")
    lines.append("### Where to find...")
    lines.append("")
    
    quick_ref = [
        ("API Routes", "src/routes/, app/api/, pages/api/"),
        ("Components", "src/components/, components/"),
        ("Business Logic", "src/services/, src/lib/"),
        ("Data Models", "src/models/, src/types/, prisma/schema.prisma"),
        ("Configuration", "src/config/, .env.example"),
        ("Tests", "src/__tests__/, tests/, *.test.ts"),
    ]
    
    for item, locations in quick_ref:
        lines.append(f"- **{item}:** `{locations}`")
    lines.append("")
    
    # Common Tasks
    lines.append("## Common Tasks")
    lines.append("")
    lines.append("### Add a new API endpoint")
    lines.append("1. Create handler in `src/routes/` or `app/api/`")
    lines.append("2. Add route definition")
    lines.append("3. Add tests in `tests/` or `__tests__/`")
    lines.append("")
    lines.append("### Add a new feature")
    lines.append("1. Create service in `src/services/`")
    lines.append("2. Add types in `src/types/`")
    lines.append("3. Create UI components in `src/components/`")
    lines.append("4. Wire up routes")
    lines.append("5. Add tests")
    lines.append("")
    
    content = "\n".join(lines)
    
    # Write to file if output specified
    if output_path:
        output_file = root / output_path
        output_file.write_text(content)
        print(f"✅ Onboarding guide written to: {output_file}")
    
    return content


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_map.py <path> [--output ONBOARDING.md]")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    if not root.exists() or not root.is_dir():
        print(f"Error: '{root}' is not a valid directory")
        sys.exit(1)
    
    # Parse output argument
    output = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output = sys.argv[idx + 1]
    
    content = generate_onboarding_guide(root, output)
    
    if not output:
        print(content)


if __name__ == "__main__":
    main()
