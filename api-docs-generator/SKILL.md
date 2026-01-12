---
name: api-docs-generator
description:
  Generate OpenAPI 3.0 specifications and API documentation from code.
  Use when user asks for API docs, OpenAPI spec, Swagger docs, endpoint documentation,
  or wants to document their REST API.
---

# API Documentation Generator

Automatically extract API routes from your codebase and generate comprehensive OpenAPI 3.0 specifications with proper schemas, examples, and descriptions.

## Quick Start

When a user asks for API documentation, follow this checklist:

```
API Documentation Progress:
- [ ] Step 1: Detect API framework and analyze routes
- [ ] Step 2: Extract endpoint definitions
- [ ] Step 3: Infer request/response schemas
- [ ] Step 4: Generate OpenAPI specification
- [ ] Step 5: Create markdown documentation
- [ ] Step 6: Add examples and descriptions
- [ ] Step 7: Validate and output
```

---

## Workflow

### Step 1: Detect Framework and Analyze Routes

Run the route analyzer to detect the API framework and find all endpoints:

```bash
python .claude/skills/api-docs-generator/scripts/analyze_routes.py .
```

**Supported Frameworks:**

- Express.js / Fastify / Hono / NestJS (Node.js)
- FastAPI / Flask / Django REST (Python)
- Gin / Echo / Chi (Go)
- Next.js API Routes / App Router

**Output includes:**

- Framework detected
- Base URL/prefix
- List of all routes with methods
- Middleware detected (auth, validation)

---

### Step 2: Extract Endpoint Definitions

For each detected endpoint, extract:

| Property     | Source                              |
| ------------ | ----------------------------------- |
| Path         | Route definition                    |
| Method       | GET, POST, PUT, PATCH, DELETE       |
| Parameters   | Path params, query params           |
| Request body | Validation schema, TypeScript types |
| Response     | Return statements, response calls   |
| Auth         | Middleware, decorators              |
| Tags         | File/folder structure               |

**Express Example:**

```typescript
// Route: POST /api/users
// Extract: path params, body schema, response type
router.post("/", validateRequest(createUserSchema), userController.create);
```

---

### Step 3: Infer Request/Response Schemas

Extract schemas from validation libraries and TypeScript types:

#### From Zod

```typescript
const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  role: z.enum(["admin", "user"]),
});
// → Infer OpenAPI schema with types, formats, constraints
```

#### From TypeScript Interfaces

```typescript
interface UserResponse {
  id: string;
  email: string;
  createdAt: Date;
}
// → Convert to OpenAPI schema
```

#### From Pydantic (Python)

```python
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
# → Convert to OpenAPI schema
```

**Schema Mapping:**

| Source Type | OpenAPI Type | Format    |
| ----------- | ------------ | --------- |
| string      | string       | -         |
| number      | number       | -         |
| boolean     | boolean      | -         |
| Date        | string       | date-time |
| email       | string       | email     |
| uuid        | string       | uuid      |
| url         | string       | uri       |
| int         | integer      | int32     |
| array       | array        | -         |
| object      | object       | -         |

---

### Step 4: Generate OpenAPI Specification

Create the OpenAPI 3.0 YAML/JSON file:

```yaml
openapi: 3.0.3
info:
  title: { { API_NAME } }
  description: { { API_DESCRIPTION } }
  version: { { VERSION } }
  contact:
    name: API Support
    email: support@example.com

servers:
  - url: http://localhost:3000
    description: Development
  - url: https://api.example.com
    description: Production

paths:
  /api/users:
    get:
      summary: List users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - $ref: "#/components/parameters/PageParam"
        - $ref: "#/components/parameters/LimitParam"
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/User"
    post:
      summary: Create user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserInput"
      responses:
        "201":
          description: Created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "400":
          $ref: "#/components/responses/BadRequest"

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        createdAt:
          type: string
          format: date-time
      required:
        - id
        - email
        - name
        - createdAt

  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1
        minimum: 1
    LimitParam:
      name: limit
      in: query
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

### Step 5: Create Markdown Documentation

Generate human-readable API documentation:

```bash
python .claude/skills/api-docs-generator/scripts/generate_markdown.py openapi.yaml --output docs/API.md
```

**Output Structure:**

````markdown
# API Documentation

## Authentication

Bearer token required for protected endpoints.

## Endpoints

### Users

#### List Users

`GET /api/users`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 20) |

**Response:**

```json
[
  {
    "id": "abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
```
````

#### Create User

`POST /api/users`

**Request Body:**

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

...

````

---

### Step 6: Add Examples and Descriptions

Enhance documentation with:

1. **Request/Response Examples**
   - Generate realistic sample data
   - Include edge cases
   - Show error responses

2. **Descriptions**
   - Summarize each endpoint's purpose
   - Document business rules
   - Note rate limits and permissions

3. **Code Snippets**
   - cURL examples
   - JavaScript/fetch examples
   - Python requests examples

---

### Step 7: Validate and Output

Validate the generated OpenAPI spec:

```bash
python .claude/skills/api-docs-generator/scripts/validate_openapi.py openapi.yaml
````

**Checks:**

- Valid OpenAPI 3.0 syntax
- All $ref references resolve
- Required fields present
- Schema consistency

**Output Files:**

```
docs/
├── openapi.yaml          # OpenAPI 3.0 spec
├── openapi.json          # JSON version
├── API.md                # Markdown docs
└── postman_collection.json  # Postman import
```

---

## Configuration

Create `.claude/api-docs-config.yaml` to customize:

```yaml
info:
  title: My API
  version: 1.0.0
  description: Backend API for MyApp

servers:
  - url: http://localhost:3000
    description: Development
  - url: https://api.myapp.com
    description: Production

defaults:
  auth: BearerAuth
  content_type: application/json
  tag_from: folder # folder, file, or manual

output:
  format: yaml # yaml or json
  path: docs/openapi.yaml
  markdown: docs/API.md
  postman: true

ignore:
  - /health
  - /metrics
  - /internal/*
```

---

## Framework-Specific Extraction

### Express.js

```typescript
// Patterns detected:
router.get("/users", handler); // Basic route
router.post("/users", validate, handler); // With middleware
app.use("/api", apiRouter); // Nested routers
```

### FastAPI

```python
# Patterns detected:
@router.get("/users", response_model=List[User])
@router.post("/users", status_code=201)
# + Pydantic models for schemas
```

### Next.js App Router

```typescript
// app/api/users/route.ts
export async function GET(request: Request) {}
export async function POST(request: Request) {}
// → Infer routes from file structure
```

### NestJS

```typescript
// Patterns detected:
@Controller('users')
@Get()
@Post()
@ApiOperation({ summary: 'List users' })  // Already has OpenAPI decorators
```

---

## Examples

### Example 1: Express API

**User asks:** "Generate OpenAPI docs for my API"

1. Run `analyze_routes.py` → Detects Express
2. Find routes in `src/routes/*.ts`
3. Extract Zod schemas from `src/schemas/`
4. Generate `openapi.yaml`
5. Create `API.md`

### Example 2: FastAPI

**User asks:** "Create Swagger documentation"

1. Detect FastAPI
2. Parse routers with decorators
3. Extract Pydantic models
4. Generate spec (FastAPI has built-in support, enhance it)

### Example 3: Next.js

**User asks:** "Document my Next.js API routes"

1. Scan `app/api/**` or `pages/api/**`
2. Infer routes from file structure
3. Parse request/response types
4. Generate documentation

---

## Tips for Best Results

1. **Use validation libraries** - Zod, Pydantic, etc. provide schema info
2. **Add TypeScript types** - Help infer request/response shapes
3. **Organize routes by resource** - Creates better tags automatically
4. **Include JSDoc/docstrings** - Used for descriptions
5. **Use consistent patterns** - Easier to detect and extract

---

## Related Skills

- **fullstack-feature-generator** - Generate APIs with built-in docs
- **codebase-onboarding** - Understand existing APIs first
