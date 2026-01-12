#!/usr/bin/env python3
"""
Generate markdown API documentation from OpenAPI spec.

Usage:
    python generate_markdown.py <openapi.yaml> --output API.md

Output:
    - Human-readable markdown documentation
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


def load_spec(file_path: Path) -> Dict:
    """Load OpenAPI spec from YAML or JSON."""
    content = file_path.read_text()
    
    if file_path.suffix in [".yaml", ".yml"]:
        # Simple YAML parser for common cases
        import yaml
        try:
            return yaml.safe_load(content)
        except ImportError:
            # Fallback to JSON if yaml not available
            print("Warning: PyYAML not installed, trying JSON format")
            return json.loads(content)
    else:
        return json.loads(content)


def resolve_ref(spec: Dict, ref: str) -> Dict:
    """Resolve a $ref to its actual schema."""
    if not ref.startswith("#/"):
        return {"type": "object"}
    
    parts = ref[2:].split("/")
    result = spec
    for part in parts:
        result = result.get(part, {})
    
    return result


def schema_to_example(spec: Dict, schema: Dict, depth: int = 0) -> any:
    """Generate example value from schema."""
    if depth > 5:
        return "..."
    
    if "$ref" in schema:
        schema = resolve_ref(spec, schema["$ref"])
    
    if "example" in schema:
        return schema["example"]
    
    schema_type = schema.get("type", "object")
    
    if schema_type == "string":
        fmt = schema.get("format", "")
        if fmt == "email":
            return "user@example.com"
        elif fmt == "uuid":
            return "550e8400-e29b-41d4-a716-446655440000"
        elif fmt == "date":
            return "2024-01-15"
        elif fmt == "date-time":
            return "2024-01-15T10:30:00Z"
        elif fmt == "uri":
            return "https://example.com"
        else:
            return "string"
    elif schema_type == "integer":
        return 1
    elif schema_type == "number":
        return 1.0
    elif schema_type == "boolean":
        return True
    elif schema_type == "array":
        items = schema.get("items", {})
        return [schema_to_example(spec, items, depth + 1)]
    elif schema_type == "object":
        result = {}
        for prop, prop_schema in schema.get("properties", {}).items():
            result[prop] = schema_to_example(spec, prop_schema, depth + 1)
        return result
    
    return None


def generate_markdown(spec: Dict) -> str:
    """Generate markdown documentation from OpenAPI spec."""
    lines = []
    
    info = spec.get("info", {})
    
    # Header
    lines.append(f"# {info.get('title', 'API Documentation')}")
    lines.append("")
    
    if info.get("description"):
        lines.append(info["description"])
        lines.append("")
    
    lines.append(f"**Version:** {info.get('version', '1.0.0')}")
    lines.append("")
    
    # Servers
    servers = spec.get("servers", [])
    if servers:
        lines.append("## Servers")
        lines.append("")
        for server in servers:
            desc = server.get("description", "")
            lines.append(f"- `{server['url']}` - {desc}")
        lines.append("")
    
    # Authentication
    security_schemes = spec.get("components", {}).get("securitySchemes", {})
    if security_schemes:
        lines.append("## Authentication")
        lines.append("")
        for name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")
            if scheme_type == "http" and scheme.get("scheme") == "bearer":
                lines.append("Bearer token authentication required.")
                lines.append("")
                lines.append("```")
                lines.append("Authorization: Bearer <token>")
                lines.append("```")
            elif scheme_type == "apiKey":
                location = scheme.get("in", "header")
                key_name = scheme.get("name", "X-API-Key")
                lines.append(f"API Key required in {location}: `{key_name}`")
        lines.append("")
    
    # Group endpoints by tag
    paths = spec.get("paths", {})
    tags = spec.get("tags", [])
    
    # Create tag -> operations mapping
    tag_operations = {}
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method not in ["get", "post", "put", "patch", "delete"]:
                continue
            
            op_tags = operation.get("tags", ["Default"])
            for tag in op_tags:
                if tag not in tag_operations:
                    tag_operations[tag] = []
                tag_operations[tag].append({
                    "path": path,
                    "method": method.upper(),
                    "operation": operation,
                })
    
    # Generate docs for each tag
    lines.append("## Endpoints")
    lines.append("")
    
    for tag_info in tags or [{"name": t} for t in tag_operations.keys()]:
        tag_name = tag_info.get("name", "Default") if isinstance(tag_info, dict) else tag_info
        if tag_name not in tag_operations:
            continue
        
        lines.append(f"### {tag_name}")
        lines.append("")
        
        for op_info in tag_operations[tag_name]:
            path = op_info["path"]
            method = op_info["method"]
            operation = op_info["operation"]
            
            # Operation header
            summary = operation.get("summary", f"{method} {path}")
            lines.append(f"#### {summary}")
            lines.append("")
            lines.append(f"```")
            lines.append(f"{method} {path}")
            lines.append(f"```")
            lines.append("")
            
            if operation.get("description"):
                lines.append(operation["description"])
                lines.append("")
            
            # Auth required?
            if operation.get("security"):
                lines.append("🔒 **Authentication required**")
                lines.append("")
            
            # Parameters
            params = operation.get("parameters", [])
            path_params = [p for p in params if p.get("in") == "path" or (
                "$ref" in p and "Path" in p["$ref"]
            )]
            query_params = [p for p in params if p.get("in") == "query" or (
                "$ref" in p and ("Page" in p["$ref"] or "Limit" in p["$ref"])
            )]
            
            if path_params:
                lines.append("**Path Parameters:**")
                lines.append("")
                lines.append("| Name | Type | Description |")
                lines.append("|------|------|-------------|")
                for param in path_params:
                    if "$ref" in param:
                        param = resolve_ref(spec, param["$ref"])
                    name = param.get("name", "")
                    schema = param.get("schema", {})
                    param_type = schema.get("type", "string")
                    desc = param.get("description", "")
                    lines.append(f"| {name} | {param_type} | {desc} |")
                lines.append("")
            
            if query_params:
                lines.append("**Query Parameters:**")
                lines.append("")
                lines.append("| Name | Type | Required | Default | Description |")
                lines.append("|------|------|----------|---------|-------------|")
                for param in query_params:
                    if "$ref" in param:
                        param = resolve_ref(spec, param["$ref"])
                    name = param.get("name", "")
                    schema = param.get("schema", {})
                    param_type = schema.get("type", "string")
                    required = "Yes" if param.get("required") else "No"
                    default = schema.get("default", "-")
                    desc = param.get("description", "")
                    lines.append(f"| {name} | {param_type} | {required} | {default} | {desc} |")
                lines.append("")
            
            # Request body
            request_body = operation.get("requestBody", {})
            if request_body:
                lines.append("**Request Body:**")
                lines.append("")
                content = request_body.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})
                
                # Generate example
                example = json_content.get("example") or schema_to_example(spec, schema)
                if example:
                    lines.append("```json")
                    lines.append(json.dumps(example, indent=2))
                    lines.append("```")
                    lines.append("")
            
            # Responses
            responses = operation.get("responses", {})
            if responses:
                lines.append("**Responses:**")
                lines.append("")
                
                for status, response in responses.items():
                    if "$ref" in response:
                        response = resolve_ref(spec, response["$ref"])
                    
                    desc = response.get("description", "")
                    lines.append(f"- `{status}` - {desc}")
                    
                    # Show example for success responses
                    if status.startswith("2"):
                        content = response.get("content", {})
                        json_content = content.get("application/json", {})
                        schema = json_content.get("schema", {})
                        
                        if schema:
                            example = json_content.get("example") or schema_to_example(spec, schema)
                            if example:
                                lines.append("")
                                lines.append("```json")
                                lines.append(json.dumps(example, indent=2))
                                lines.append("```")
                
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # Schemas
    schemas = spec.get("components", {}).get("schemas", {})
    if schemas:
        lines.append("## Schemas")
        lines.append("")
        
        for name, schema in schemas.items():
            if name == "Error":
                continue  # Skip error schema
            
            lines.append(f"### {name}")
            lines.append("")
            lines.append("```json")
            example = schema_to_example(spec, schema)
            lines.append(json.dumps(example, indent=2))
            lines.append("```")
            lines.append("")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_markdown.py <openapi.yaml> [--output API.md]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Load spec
    try:
        spec = load_spec(input_path)
    except Exception as e:
        print(f"Error loading spec: {e}")
        sys.exit(1)
    
    # Generate markdown
    markdown = generate_markdown(spec)
    
    # Output
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    if output_path:
        Path(output_path).write_text(markdown)
        print(f"✅ Markdown docs written to: {output_path}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
