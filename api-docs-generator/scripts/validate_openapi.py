#!/usr/bin/env python3
"""
Validate OpenAPI 3.0 specification.

Usage:
    python validate_openapi.py <openapi.yaml>

Checks:
    - Valid OpenAPI 3.0 structure
    - All $ref references resolve
    - Required fields present
    - Schema consistency
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def load_spec(file_path: Path) -> Dict:
    """Load OpenAPI spec from YAML or JSON."""
    content = file_path.read_text()
    
    if file_path.suffix in [".yaml", ".yml"]:
        try:
            import yaml
            return yaml.safe_load(content)
        except ImportError:
            print("Warning: PyYAML not installed")
            return json.loads(content)
    else:
        return json.loads(content)


def validate_refs(spec: Dict) -> List[str]:
    """Validate all $ref references resolve."""
    errors = []
    
    def check_ref(obj: any, path: str):
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if ref.startswith("#/"):
                    # Validate internal ref
                    parts = ref[2:].split("/")
                    target = spec
                    for part in parts:
                        if isinstance(target, dict) and part in target:
                            target = target[part]
                        else:
                            errors.append(f"{path}: Reference not found: {ref}")
                            break
            
            for key, value in obj.items():
                check_ref(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_ref(item, f"{path}[{i}]")
    
    check_ref(spec, "root")
    return errors


def validate_structure(spec: Dict) -> List[str]:
    """Validate OpenAPI structure."""
    errors = []
    
    # Required top-level fields
    if "openapi" not in spec:
        errors.append("Missing required field: openapi")
    elif not spec["openapi"].startswith("3."):
        errors.append(f"Invalid OpenAPI version: {spec['openapi']} (expected 3.x)")
    
    if "info" not in spec:
        errors.append("Missing required field: info")
    else:
        if "title" not in spec["info"]:
            errors.append("Missing required field: info.title")
        if "version" not in spec["info"]:
            errors.append("Missing required field: info.version")
    
    if "paths" not in spec:
        errors.append("Missing required field: paths")
    
    return errors


def validate_paths(spec: Dict) -> List[str]:
    """Validate path definitions."""
    errors = []
    paths = spec.get("paths", {})
    
    for path, methods in paths.items():
        # Path should start with /
        if not path.startswith("/"):
            errors.append(f"Path should start with /: {path}")
        
        for method, operation in methods.items():
            if method not in ["get", "post", "put", "patch", "delete", "options", "head", "trace", "parameters"]:
                if method != "$ref":
                    errors.append(f"Invalid HTTP method: {method} at {path}")
                continue
            
            if method == "parameters":
                continue
            
            if not isinstance(operation, dict):
                continue
            
            # Check responses
            if "responses" not in operation:
                errors.append(f"Missing responses: {method.upper()} {path}")
            else:
                responses = operation["responses"]
                if not any(str(code).startswith("2") for code in responses.keys()):
                    errors.append(f"No success response (2xx): {method.upper()} {path}")
            
            # Check path params are defined
            path_params = re.findall(r'\{(\w+)\}', path)
            defined_params = [
                p.get("name") for p in operation.get("parameters", [])
                if p.get("in") == "path" or (
                    "$ref" in p and "Path" in p["$ref"]
                )
            ]
            
            for param in path_params:
                # Check if defined or inherited from path level
                path_level_params = [
                    p.get("name") for p in methods.get("parameters", [])
                    if p.get("in") == "path"
                ]
                if param not in defined_params and param not in path_level_params:
                    errors.append(f"Undefined path parameter: {{{param}}} at {method.upper()} {path}")
    
    return errors


def validate_schemas(spec: Dict) -> List[str]:
    """Validate component schemas."""
    errors = []
    schemas = spec.get("components", {}).get("schemas", {})
    
    for name, schema in schemas.items():
        if not isinstance(schema, dict):
            errors.append(f"Invalid schema: {name}")
            continue
        
        # Check type is valid
        schema_type = schema.get("type")
        if schema_type and schema_type not in ["string", "number", "integer", "boolean", "array", "object", "null"]:
            errors.append(f"Invalid schema type: {schema_type} in {name}")
        
        # Array should have items
        if schema_type == "array" and "items" not in schema:
            errors.append(f"Array schema missing items: {name}")
        
        # Object should have properties
        if schema_type == "object" and "properties" not in schema and "additionalProperties" not in schema:
            # This is a warning, not error
            pass
    
    return errors


def validate_security(spec: Dict) -> List[str]:
    """Validate security definitions."""
    errors = []
    
    security_schemes = spec.get("components", {}).get("securitySchemes", {})
    
    # Check global security references
    global_security = spec.get("security", [])
    for sec in global_security:
        for scheme_name in sec.keys():
            if scheme_name not in security_schemes:
                errors.append(f"Undefined security scheme: {scheme_name}")
    
    # Check operation-level security
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            op_security = operation.get("security", [])
            for sec in op_security:
                for scheme_name in sec.keys():
                    if scheme_name not in security_schemes:
                        errors.append(f"Undefined security scheme: {scheme_name} at {method.upper()} {path}")
    
    return errors


def format_results(results: Dict) -> str:
    """Format validation results."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("OPENAPI VALIDATION RESULTS")
    lines.append("=" * 60)
    
    total_errors = sum(len(v) for v in results.values())
    
    if total_errors == 0:
        lines.append("\n✅ Validation passed! No errors found.")
    else:
        lines.append(f"\n❌ Found {total_errors} error(s)")
        
        for category, errors in results.items():
            if errors:
                lines.append(f"\n{category}:")
                for error in errors:
                    lines.append(f"   ❌ {error}")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_openapi.py <openapi.yaml>")
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
    
    # Run validations
    results = {
        "Structure": validate_structure(spec),
        "References": validate_refs(spec),
        "Paths": validate_paths(spec),
        "Schemas": validate_schemas(spec),
        "Security": validate_security(spec),
    }
    
    # Output
    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results))
    
    # Exit code
    total_errors = sum(len(v) for v in results.values())
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
