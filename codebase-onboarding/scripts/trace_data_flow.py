#!/usr/bin/env python3
"""
Trace data flow through a codebase for a specific feature.

Usage:
    python trace_data_flow.py <path> --feature "user authentication"

Output:
    - Input sources (API, CLI, events)
    - Processing steps
    - Data transformations
    - Output destinations
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", ".nuxt",
    "dist", "build", "out", ".cache", "coverage", "vendor",
    ".idea", ".venv", "venv", "env"
}

# Common data flow patterns
PATTERNS = {
    "input": {
        "http_request": [
            r"req\.(body|params|query|headers)",
            r"request\.(json|form|args|data)",
            r"ctx\.(request|params|query)",
        ],
        "file_read": [
            r"fs\.(readFile|readFileSync|createReadStream)",
            r"open\(.+['\"]r['\"]",
            r"Path\(.+\)\.read_",
        ],
        "database_read": [
            r"\.(find|findOne|findMany|findFirst|select)\s*\(",
            r"\.query\s*\(",
            r"SELECT\s+.+\s+FROM",
        ],
        "env_vars": [
            r"process\.env\.\w+",
            r"os\.environ\.get\s*\(",
            r"os\.Getenv\s*\(",
        ],
    },
    "transform": {
        "mapping": [
            r"\.(map|filter|reduce)\s*\(",
            r"list\s+comprehension",
        ],
        "validation": [
            r"\.(validate|parse|safeParse)\s*\(",
            r"validator\.",
            r"@validator",
        ],
        "serialization": [
            r"JSON\.(parse|stringify)",
            r"json\.(loads|dumps)",
            r"Marshal|Unmarshal",
        ],
    },
    "output": {
        "http_response": [
            r"res\.(json|send|status|render)",
            r"return\s+(jsonify|Response|JSONResponse)",
            r"ctx\.JSON|ctx\.String",
        ],
        "file_write": [
            r"fs\.(writeFile|writeFileSync|createWriteStream)",
            r"open\(.+['\"]w['\"]",
            r"Path\(.+\)\.write_",
        ],
        "database_write": [
            r"\.(create|update|delete|insert|save)\s*\(",
            r"\.execute\s*\(",
            r"INSERT|UPDATE|DELETE",
        ],
        "logging": [
            r"console\.(log|error|warn|info)",
            r"logger\.\w+\s*\(",
            r"log\.(Info|Error|Warn|Debug)",
        ],
    }
}

# Feature keywords for common features
FEATURE_KEYWORDS = {
    "authentication": ["auth", "login", "logout", "token", "jwt", "session", "password", "credential"],
    "user": ["user", "profile", "account", "member"],
    "payment": ["payment", "stripe", "billing", "invoice", "subscription"],
    "notification": ["notification", "email", "sms", "push", "alert"],
    "upload": ["upload", "file", "image", "media", "s3", "storage"],
    "api": ["api", "route", "endpoint", "handler", "controller"],
    "database": ["database", "db", "model", "schema", "migration"],
}


def parse_feature(feature: str) -> List[str]:
    """Parse feature name into search keywords."""
    # Normalize
    feature_lower = feature.lower()
    
    # Check known features
    for key, keywords in FEATURE_KEYWORDS.items():
        if key in feature_lower or any(k in feature_lower for k in keywords):
            return keywords
    
    # Extract words from feature
    words = re.findall(r'\w+', feature_lower)
    return words


def find_relevant_files(root: Path, keywords: List[str]) -> List[Path]:
    """Find files related to the feature."""
    relevant = []
    
    for file_path in root.rglob("*"):
        if any(ignore in str(file_path) for ignore in IGNORE_DIRS):
            continue
        
        if file_path.suffix not in [".js", ".ts", ".py", ".go", ".tsx", ".jsx"]:
            continue
        
        path_str = str(file_path).lower()
        
        # Check if filename contains keywords
        if any(kw in path_str for kw in keywords):
            relevant.append(file_path)
            continue
        
        # Check file content
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
            matches = sum(1 for kw in keywords if kw in content)
            if matches >= 2:  # At least 2 keyword matches
                relevant.append(file_path)
        except Exception:
            pass
    
    return relevant


def analyze_data_flow(file_path: Path, root: Path) -> Dict:
    """Analyze data flow patterns in a file."""
    result = {
        "path": str(file_path.relative_to(root)),
        "inputs": [],
        "transforms": [],
        "outputs": [],
        "dependencies": [],
    }
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        
        # Find imports/dependencies
        import_patterns = [
            r"import\s+.+\s+from\s+['\"]([^'\"]+)['\"]",
            r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"from\s+(\S+)\s+import",
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            result["dependencies"].extend(matches)
        
        # Analyze patterns
        for category, patterns in PATTERNS.items():
            for pattern_type, regexes in patterns.items():
                for regex in regexes:
                    for i, line in enumerate(lines, 1):
                        if re.search(regex, line, re.IGNORECASE):
                            entry = {
                                "type": pattern_type,
                                "line": i,
                                "code": line.strip()[:100]
                            }
                            
                            if category == "input":
                                result["inputs"].append(entry)
                            elif category == "transform":
                                result["transforms"].append(entry)
                            elif category == "output":
                                result["outputs"].append(entry)
    except Exception as e:
        result["error"] = str(e)
    
    return result


def build_flow_graph(analyses: List[Dict]) -> Dict:
    """Build a data flow graph from file analyses."""
    graph = {
        "nodes": [],
        "edges": [],
        "summary": {
            "total_inputs": 0,
            "total_transforms": 0,
            "total_outputs": 0,
        }
    }
    
    for analysis in analyses:
        node = {
            "id": analysis["path"],
            "inputs": len(analysis.get("inputs", [])),
            "transforms": len(analysis.get("transforms", [])),
            "outputs": len(analysis.get("outputs", [])),
        }
        graph["nodes"].append(node)
        
        graph["summary"]["total_inputs"] += node["inputs"]
        graph["summary"]["total_transforms"] += node["transforms"]
        graph["summary"]["total_outputs"] += node["outputs"]
        
        # Create edges based on dependencies
        for dep in analysis.get("dependencies", []):
            if dep.startswith(".") or dep.startswith("@"):
                # Local dependency
                for other in analyses:
                    if dep.replace("./", "").replace("../", "") in other["path"]:
                        graph["edges"].append({
                            "from": analysis["path"],
                            "to": other["path"],
                            "type": "imports"
                        })
    
    return graph


def format_output(result: Dict) -> str:
    """Format results as readable text."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("DATA FLOW ANALYSIS")
    lines.append("=" * 60)
    
    lines.append(f"\n🔍 Feature: {result['feature']}")
    lines.append(f"📁 Relevant Files: {len(result['files'])}")
    
    # Summary
    summary = result["graph"]["summary"]
    lines.append(f"\n📊 Summary:")
    lines.append(f"   Inputs:     {summary['total_inputs']}")
    lines.append(f"   Transforms: {summary['total_transforms']}")
    lines.append(f"   Outputs:    {summary['total_outputs']}")
    
    # Data flow diagram
    lines.append(f"\n📈 Data Flow:")
    lines.append("""
    ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
    │   INPUTS    │────▶│  TRANSFORMS  │────▶│   OUTPUTS   │
    │             │     │              │     │             │
    │ • HTTP Req  │     │ • Validation │     │ • HTTP Res  │
    │ • DB Read   │     │ • Mapping    │     │ • DB Write  │
    │ • File Read │     │ • Serialize  │     │ • Logging   │
    └─────────────┘     └──────────────┘     └─────────────┘
    """)
    
    # File details
    for analysis in result["analyses"][:5]:
        lines.append(f"\n📄 {analysis['path']}")
        
        if analysis.get("inputs"):
            lines.append(f"   Inputs:")
            for inp in analysis["inputs"][:3]:
                lines.append(f"     L{inp['line']}: {inp['type']}")
        
        if analysis.get("outputs"):
            lines.append(f"   Outputs:")
            for out in analysis["outputs"][:3]:
                lines.append(f"     L{out['line']}: {out['type']}")
    
    if len(result["analyses"]) > 5:
        lines.append(f"\n   ... and {len(result['analyses']) - 5} more files")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python trace_data_flow.py <path> --feature <feature>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    # Parse feature argument
    feature = "general"
    if "--feature" in sys.argv:
        idx = sys.argv.index("--feature")
        if idx + 1 < len(sys.argv):
            feature = sys.argv[idx + 1]
    
    if not root.exists() or not root.is_dir():
        print(f"Error: '{root}' is not a valid directory")
        sys.exit(1)
    
    # Analyze
    keywords = parse_feature(feature)
    relevant_files = find_relevant_files(root, keywords)
    analyses = [analyze_data_flow(f, root) for f in relevant_files]
    graph = build_flow_graph(analyses)
    
    result = {
        "feature": feature,
        "keywords": keywords,
        "files": [str(f.relative_to(root)) for f in relevant_files],
        "analyses": analyses,
        "graph": graph
    }
    
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
