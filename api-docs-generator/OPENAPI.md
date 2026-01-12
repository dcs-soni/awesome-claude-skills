# OpenAPI 3.0 Reference

Quick reference for generating valid OpenAPI specifications.

---

## Specification Structure

```yaml
openapi: 3.0.3 # Required: OpenAPI version
info: # Required: API metadata
  title: API Name
  version: 1.0.0
servers: # API server URLs
  - url: https://api.example.com
paths: # API endpoints
  /resource:
    get: ...
components: # Reusable components
  schemas: ...
  parameters: ...
  responses: ...
security: # Global security
  - BearerAuth: []
tags: # Endpoint grouping
  - name: Users
```

---

## Path Operations

### Methods

```yaml
/users:
  get: # Read collection
  post: # Create resource
/users/{id}:
  get: # Read single
  put: # Replace
  patch: # Partial update
  delete: # Remove
```

### Operation Structure

```yaml
get:
  summary: Short description # Required
  description: Detailed explanation # Optional
  operationId: listUsers # Unique ID
  tags:
    - Users # Grouping
  parameters: # Inputs
    - $ref: "#/components/parameters/Id"
  requestBody: # For POST/PUT/PATCH
    required: true
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/Input"
  responses: # Required
    "200":
      description: Success
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Output"
  security: # Override global
    - BearerAuth: []
  deprecated: false # Mark as deprecated
```

---

## Parameters

### Path Parameters

```yaml
parameters:
  - name: id
    in: path
    required: true
    description: Resource ID
    schema:
      type: string
      format: uuid
```

### Query Parameters

```yaml
parameters:
  - name: page
    in: query
    required: false
    schema:
      type: integer
      default: 1
      minimum: 1
  - name: search
    in: query
    schema:
      type: string
```

### Header Parameters

```yaml
parameters:
  - name: X-Request-ID
    in: header
    schema:
      type: string
      format: uuid
```

---

## Request Body

```yaml
requestBody:
  required: true
  description: User creation payload
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/CreateUser"
      example:
        email: user@example.com
        name: John Doe
```

---

## Responses

### Success Responses

```yaml
responses:
  "200":
    description: Successful response
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/User"
  "201":
    description: Created
    headers:
      Location:
        schema:
          type: string
  "204":
    description: No content
```

### Error Responses

```yaml
responses:
  "400":
    description: Bad request
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/Error"
  "401":
    description: Unauthorized
  "403":
    description: Forbidden
  "404":
    description: Not found
  "422":
    description: Validation error
  "500":
    description: Internal server error
```

---

## Schemas

### Basic Types

```yaml
schemas:
  StringField:
    type: string
    minLength: 1
    maxLength: 255
    pattern: "^[a-zA-Z]+$"

  NumberField:
    type: number
    minimum: 0
    maximum: 100

  IntegerField:
    type: integer
    format: int32 # or int64

  BooleanField:
    type: boolean
    default: false

  DateField:
    type: string
    format: date # 2024-01-15

  DateTimeField:
    type: string
    format: date-time # 2024-01-15T10:30:00Z
```

### String Formats

| Format      | Example                              |
| ----------- | ------------------------------------ |
| `date`      | 2024-01-15                           |
| `date-time` | 2024-01-15T10:30:00Z                 |
| `email`     | user@example.com                     |
| `uri`       | https://example.com                  |
| `uuid`      | 550e8400-e29b-41d4-a716-446655440000 |
| `password`  | (masked in docs)                     |
| `byte`      | base64 encoded                       |
| `binary`    | binary data                          |

### Objects

```yaml
schemas:
  User:
    type: object
    required:
      - id
      - email
    properties:
      id:
        type: string
        format: uuid
        readOnly: true
      email:
        type: string
        format: email
      name:
        type: string
        nullable: true
      role:
        type: string
        enum: [admin, user, guest]
        default: user
      createdAt:
        type: string
        format: date-time
        readOnly: true
```

### Arrays

```yaml
schemas:
  UserList:
    type: array
    items:
      $ref: "#/components/schemas/User"
    minItems: 0
    maxItems: 100
```

### Composition

```yaml
schemas:
  # allOf - Combine schemas (AND)
  AdminUser:
    allOf:
      - $ref: "#/components/schemas/User"
      - type: object
        properties:
          permissions:
            type: array
            items:
              type: string

  # oneOf - One of multiple schemas (XOR)
  Pet:
    oneOf:
      - $ref: "#/components/schemas/Dog"
      - $ref: "#/components/schemas/Cat"
    discriminator:
      propertyName: type

  # anyOf - Any combination (OR)
  SearchResult:
    anyOf:
      - $ref: "#/components/schemas/User"
      - $ref: "#/components/schemas/Post"
```

---

## Security Schemes

### Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

### API Key

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - ApiKeyAuth: []
```

### OAuth2

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
            write: Write access
```

### Multiple Schemes

```yaml
# Require both (AND)
security:
  - BearerAuth: []
    ApiKeyAuth: []

# Require either (OR)
security:
  - BearerAuth: []
  - ApiKeyAuth: []
```

---

## Reusable Components

### Define Once

```yaml
components:
  parameters:
    IdParam:
      name: id
      in: path
      required: true
      schema:
        type: string
        format: uuid
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1

  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"

  schemas:
    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
      required:
        - code
        - message
```

### Reference

```yaml
paths:
  /users/{id}:
    get:
      parameters:
        - $ref: "#/components/parameters/IdParam"
      responses:
        "404":
          $ref: "#/components/responses/NotFound"
```

---

## Examples

### Inline Examples

```yaml
schema:
  type: object
  properties:
    email:
      type: string
      example: user@example.com
    name:
      type: string
      example: John Doe
```

### Named Examples

```yaml
content:
  application/json:
    schema:
      $ref: "#/components/schemas/User"
    examples:
      admin:
        summary: Admin user
        value:
          id: abc123
          email: admin@example.com
          role: admin
      guest:
        summary: Guest user
        value:
          id: xyz789
          email: guest@example.com
          role: guest
```

---

## Tags

```yaml
tags:
  - name: Users
    description: User management endpoints
  - name: Posts
    description: Blog post operations
    externalDocs:
      description: Learn more
      url: https://docs.example.com/posts

paths:
  /users:
    get:
      tags:
        - Users
```

---

## Common Patterns

### Pagination Response

```yaml
schemas:
  PaginatedResponse:
    type: object
    properties:
      data:
        type: array
        items: {}
      meta:
        type: object
        properties:
          total:
            type: integer
          page:
            type: integer
          limit:
            type: integer
          totalPages:
            type: integer
```

### Error Response

```yaml
schemas:
  ApiError:
    type: object
    required:
      - status
      - code
      - message
    properties:
      status:
        type: integer
      code:
        type: string
      message:
        type: string
      details:
        type: object
        additionalProperties:
          type: array
          items:
            type: string
```

### Timestamps

```yaml
schemas:
  Timestamps:
    type: object
    properties:
      createdAt:
        type: string
        format: date-time
        readOnly: true
      updatedAt:
        type: string
        format: date-time
        readOnly: true
```
