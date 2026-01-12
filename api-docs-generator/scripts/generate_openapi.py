#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specification from analyzed routes.

Usage:
    python generate_openapi.py <routes.json> --output openapi.yaml

Output:
    - OpenAPI 3.0 specification in YAML or JSON format
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Default OpenAPI template
OPENAPI_TEMPLATE = {
    "openapi": "3.0.3",
    "info": {
        "title": "API Documentation",
        "version": "1.0.0",
        "description": "Auto-generated API documentation",
    },
    "servers": [
        {"url": "http://localhost:3000", "description": "Development"},
    ],
    "paths": {},
    "components": {
        "schemas": {},
        "parameters": {
            "PageParam": {
                "name": "page",
                "in": "query",
                "schema": {"type": "integer", "default": 1, "minimum": 1},
            },
            "LimitParam": {
                "name": "limit",
                "in": "query",
                "schema": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
            },
        },
        "responses": {
            "BadRequest": {
                "description": "Invalid request data",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"}
                    }
                },
            },
            "Unauthorized": {"description": "Authentication required"},
            "Forbidden": {"description": "Insufficient permissions"},
            "NotFound": {"description": "Resource not found"},
        },
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
    },
    "tags": [],
}


def path_to_openapi(path: str) -> str:
    """Convert route path to OpenAPI format."""
    # Express :param -> OpenAPI {param}
    path = re.sub(r':(\w+)', r'{\1}', path)
    return path


def extract_path_params(path: str) -> List[Dict]:
    """Extract path parameters from route path."""
    params = []
    param_matches = re.findall(r'\{(\w+)\}', path)
    
    for param in param_matches:
        params.append({
            "name": param,
            "in": "path",
            "required": True,
            "schema": {
                "type": "string",
                "format": "uuid" if param in ["id", "userId", "postId"] else None,
            },
        })
    
    # Clean up None values
    for param in params:
        if param["schema"].get("format") is None:
            del param["schema"]["format"]
    
    return params


def infer_tag(path: str, file_path: str) -> str:
    """Infer tag from path or file."""
    # Try to get from path
    parts = path.strip("/").split("/")
    
    # Skip 'api' prefix
    if parts and parts[0] == "api":
        parts = parts[1:]
    
    if parts:
        resource = parts[0]
        # Capitalize and singularize
        tag = resource.replace("-", " ").replace("_", " ").title()
        return tag
    
    # Fall back to file name
    if file_path:
        file_name = Path(file_path).stem
        return file_name.replace(".routes", "").replace(".controller", "").title()
    
    return "Default"


def method_to_operation(method: str, path: str, route: Dict) -> Dict:
    """Convert route to OpenAPI operation."""
    resource = infer_tag(path, route.get("file", ""))
    resource_singular = resource.rstrip("s")
    
    operation = {
        "summary": "",
        "operationId": "",
        "tags": [resource],
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    }
                }
            }
        }
    }
    
    # Generate summary and operationId based on method
    path_params = extract_path_params(path)
    is_single = any(p["name"] == "id" for p in path_params)
    
    if method == "GET":
        if is_single:
            operation["summary"] = f"Get {resource_singular} by ID"
            operation["operationId"] = f"get{resource_singular}ById"
        else:
            operation["summary"] = f"List {resource}"
            operation["operationId"] = f"list{resource}"
            operation["parameters"] = [
                {"$ref": "#/components/parameters/PageParam"},
                {"$ref": "#/components/parameters/LimitParam"},
            ]
    elif method == "POST":
        operation["summary"] = f"Create {resource_singular}"
        operation["operationId"] = f"create{resource_singular}"
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/Create{resource_singular}Input"}
                }
            }
        }
        operation["responses"]["201"] = {
            "description": "Created",
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/{resource_singular}"}
                }
            }
        }
        operation["responses"]["400"] = {"$ref": "#/components/responses/BadRequest"}
    elif method == "PUT" or method == "PATCH":
        operation["summary"] = f"Update {resource_singular}"
        operation["operationId"] = f"update{resource_singular}"
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/Update{resource_singular}Input"}
                }
            }
        }
    elif method == "DELETE":
        operation["summary"] = f"Delete {resource_singular}"
        operation["operationId"] = f"delete{resource_singular}"
        operation["responses"]["204"] = {"description": "Deleted"}
    
    # Add auth if detected
    if "auth" in route.get("middleware", []):
        operation["security"] = [{"BearerAuth": []}]
    
    # Add path parameters
    if path_params:
        if "parameters" not in operation:
            operation["parameters"] = []
        operation["parameters"].extend(path_params)
    
    return operation


def generate_schema_stub(name: str) -> Dict:
    """Generate a stub schema for a resource."""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "createdAt": {"type": "string", "format": "date-time"},
            "updatedAt": {"type": "string", "format": "date-time"},
        },
        "required": ["id"],
    }


def generate_openapi(routes: List[Dict], config: Dict = None) -> Dict:
    """Generate OpenAPI specification from routes."""
    spec = OPENAPI_TEMPLATE.copy()
    spec["paths"] = {}
    spec["components"] = dict(spec["components"])
    spec["components"]["schemas"] = {
        "Error": {
            "type": "object",
            "properties": {
                "status": {"type": "integer"},
                "code": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["status", "code", "message"],
        }
    }
    
    # Apply config
    if config:
        if "info" in config:
            spec["info"].update(config["info"])
        if "servers" in config:
            spec["servers"] = config["servers"]
    
    tags_set = set()
    
    # Group routes by path
    path_routes = {}
    for route in routes:
        path = path_to_openapi(route["path"])
        if path not in path_routes:
            path_routes[path] = {}
        
        methods = route["method"].split(",")
        for method in methods:
            method = method.strip().lower()
            if method in ["get", "post", "put", "patch", "delete"]:
                path_routes[path][method] = route
    
    # Generate operations
    for path, methods in path_routes.items():
        spec["paths"][path] = {}
        
        for method, route in methods.items():
            operation = method_to_operation(method.upper(), path, route)
            spec["paths"][path][method] = operation
            
            # Collect tags
            for tag in operation.get("tags", []):
                tags_set.add(tag)
            
            # Generate schema stubs
            resource = operation["tags"][0] if operation.get("tags") else "Resource"
            resource_singular = resource.rstrip("s")
            
            schema_names = [
                resource_singular,
                f"Create{resource_singular}Input",
                f"Update{resource_singular}Input",
            ]
            
            for schema_name in schema_names:
                if schema_name not in spec["components"]["schemas"]:
                    spec["components"]["schemas"][schema_name] = generate_schema_stub(schema_name)
    
    # Generate tags
    spec["tags"] = [{"name": tag} for tag in sorted(tags_set)]
    
    return spec


def to_yaml(obj: Dict, indent: int = 0) -> str:
    """Convert dict to YAML string (simple implementation)."""
    lines = []
    prefix = "  " * indent
    
    for key, value in obj.items():
        if value is None:
            continue
        elif isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(to_yaml(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{prefix}  -")
                    # Inline first key
                    first = True
                    for k, v in item.items():
                        if first:
                            if isinstance(v, (dict, list)):
                                lines.append(f"{prefix}    {k}:")
                                lines.append(to_yaml(v, indent + 3))
                            else:
                                lines.append(f"{prefix}    {k}: {format_yaml_value(v)}")
                            first = False
                        else:
                            if isinstance(v, (dict, list)):
                                lines.append(f"{prefix}    {k}:")
                                lines.append(to_yaml(v, indent + 3))
                            else:
                                lines.append(f"{prefix}    {k}: {format_yaml_value(v)}")
                else:
                    lines.append(f"{prefix}  - {format_yaml_value(item)}")
        else:
            lines.append(f"{prefix}{key}: {format_yaml_value(value)}")
    
    return "\n".join(lines)


def format_yaml_value(value) -> str:
    """Format a value for YAML output."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        if any(c in value for c in [":", "#", "'", '"', "\n", "{", "}"]):
            return f'"{value}"'
        return value
    elif value is None:
        return "null"
    else:
        return str(value)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_openapi.py <routes.json> [--output file.yaml]")
        print("       python generate_openapi.py <path> [--output file.yaml]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    # Check if input is a routes JSON or a directory to analyze
    if input_path.suffix == ".json":
        routes = json.loads(input_path.read_text())
        if isinstance(routes, dict) and "routes" in routes:
            routes = routes["routes"]
    else:
        # Run route analysis
        print("Analyzing routes...")
        from analyze_routes import detect_framework, find_route_files, extract_routes, extract_nextjs_routes
        
        root = input_path.resolve()
        framework = detect_framework(root)
        
        if framework == "nextjs":
            routes = extract_nextjs_routes(root)
        elif framework:
            files = find_route_files(root, framework)
            routes = []
            for f in files:
                routes.extend(extract_routes(f, framework))
        else:
            routes = []
    
    # Load config if exists
    config = None
    config_path = input_path / ".claude" / "api-docs-config.yaml" if input_path.is_dir() else None
    
    # Generate OpenAPI
    spec = generate_openapi(routes, config)
    
    # Output
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    if "--json" in sys.argv:
        output = json.dumps(spec, indent=2)
    else:
        output = to_yaml(spec)
    
    if output_path:
        Path(output_path).write_text(output)
        print(f"✅ OpenAPI spec written to: {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
