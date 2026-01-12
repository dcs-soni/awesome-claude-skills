# API Documentation Generator

A Claude Code Skill for automatically generating OpenAPI 3.0 specifications and API documentation from your codebase.

## What It Does

This skill analyzes your API routes and generates:

- **OpenAPI 3.0 spec** (YAML/JSON)
- **Markdown documentation** with examples
- **Postman collection** (optional)
- **cURL/JavaScript examples**

## Supported Frameworks

| Language | Frameworks                     |
| -------- | ------------------------------ |
| Node.js  | Express, Fastify, Hono, NestJS |
| Python   | FastAPI, Flask, Django REST    |
| Go       | Gin, Echo, Chi                 |
| Next.js  | App Router, Pages Router       |

## Installation

Copy to your project:

```bash
cp -r api-docs-generator /path/to/your-project/.claude/skills/
```

Or install globally:

```bash
cp -r api-docs-generator ~/.claude/skills/
```

## Usage

### Example Prompts

```
"Generate OpenAPI docs for my API"

"Create Swagger documentation"

"Document all my API endpoints"

"Generate API.md for this project"
```

### Generated Files

```
docs/
├── openapi.yaml          # OpenAPI 3.0 spec
├── openapi.json          # JSON version
├── API.md                # Markdown docs
└── postman_collection.json
```

## Workflow

| Step | Action                         |
| ---- | ------------------------------ |
| 1    | Detect API framework           |
| 2    | Extract route definitions      |
| 3    | Infer request/response schemas |
| 4    | Generate OpenAPI spec          |
| 5    | Create markdown docs           |
| 6    | Add examples                   |
| 7    | Validate output                |

## Scripts

| Script                 | Purpose                | Usage                                                              |
| ---------------------- | ---------------------- | ------------------------------------------------------------------ |
| `analyze_routes.py`    | Find all API endpoints | `python scripts/analyze_routes.py .`                               |
| `generate_openapi.py`  | Generate OpenAPI spec  | `python scripts/generate_openapi.py . --output openapi.yaml`       |
| `generate_markdown.py` | Create markdown docs   | `python scripts/generate_markdown.py openapi.yaml --output API.md` |
| `validate_openapi.py`  | Validate the spec      | `python scripts/validate_openapi.py openapi.yaml`                  |

## Configuration

Create `.claude/api-docs-config.yaml`:

```yaml
info:
  title: My API
  version: 1.0.0

servers:
  - url: http://localhost:3000
  - url: https://api.myapp.com

defaults:
  auth: BearerAuth

ignore:
  - /health
  - /metrics
```

## Reference Files

| File                         | Description                 |
| ---------------------------- | --------------------------- |
| [OPENAPI.md](./OPENAPI.md)   | OpenAPI 3.0 reference guide |
| [EXAMPLES.md](./EXAMPLES.md) | Sample outputs              |

## Features

- **Auto-detection** of frameworks and patterns
- **Schema inference** from Zod, Pydantic, TypeScript
- **Auth detection** (JWT, API Key, OAuth)
- **Example generation** with realistic data
- **Validation** before output

## Requirements

- Python 3.7+
- PyYAML (`pip install pyyaml`) - optional

## License

MIT
