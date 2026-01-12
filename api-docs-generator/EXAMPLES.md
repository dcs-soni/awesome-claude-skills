# API Documentation Examples

Real-world examples of generated API documentation.

---

## Example 1: User Management API

### Input Routes (Express)

```typescript
// src/routes/users.routes.ts
router.get("/", auth, userController.list);
router.get("/:id", auth, userController.getById);
router.post(
  "/",
  auth,
  validateRequest(createUserSchema),
  userController.create
);
router.put(
  "/:id",
  auth,
  validateRequest(updateUserSchema),
  userController.update
);
router.delete("/:id", auth, requireRole("admin"), userController.delete);
```

### Generated OpenAPI

```yaml
openapi: 3.0.3
info:
  title: User Management API
  version: 1.0.0

paths:
  /api/users:
    get:
      summary: List users
      operationId: listUsers
      tags: [Users]
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        "200":
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/User"
        "401":
          $ref: "#/components/responses/Unauthorized"

    post:
      summary: Create user
      operationId: createUser
      tags: [Users]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserInput"
            example:
              email: newuser@example.com
              name: John Doe
              role: user
      responses:
        "201":
          description: User created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "400":
          $ref: "#/components/responses/BadRequest"
        "401":
          $ref: "#/components/responses/Unauthorized"

  /api/users/{id}:
    parameters:
      - $ref: "#/components/parameters/UserId"

    get:
      summary: Get user by ID
      operationId: getUserById
      tags: [Users]
      security:
        - BearerAuth: []
      responses:
        "200":
          description: User details
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "404":
          $ref: "#/components/responses/NotFound"

    put:
      summary: Update user
      operationId: updateUser
      tags: [Users]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UpdateUserInput"
      responses:
        "200":
          description: User updated
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"

    delete:
      summary: Delete user
      operationId: deleteUser
      tags: [Users]
      security:
        - BearerAuth: []
      description: Requires admin role
      responses:
        "204":
          description: User deleted
        "403":
          $ref: "#/components/responses/Forbidden"

components:
  schemas:
    User:
      type: object
      required: [id, email, name, role, createdAt]
      properties:
        id:
          type: string
          format: uuid
          example: 550e8400-e29b-41d4-a716-446655440000
        email:
          type: string
          format: email
          example: user@example.com
        name:
          type: string
          example: John Doe
        role:
          type: string
          enum: [admin, user, guest]
          example: user
        createdAt:
          type: string
          format: date-time
          example: "2024-01-15T10:30:00Z"
        updatedAt:
          type: string
          format: date-time

    CreateUserInput:
      type: object
      required: [email, name]
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 2
          maxLength: 100
        role:
          type: string
          enum: [admin, user, guest]
          default: user

    UpdateUserInput:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 2
          maxLength: 100
        role:
          type: string
          enum: [admin, user, guest]

  parameters:
    UserId:
      name: id
      in: path
      required: true
      schema:
        type: string
        format: uuid

  responses:
    BadRequest:
      description: Invalid request data
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    Unauthorized:
      description: Authentication required
    Forbidden:
      description: Insufficient permissions
    NotFound:
      description: Resource not found

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Example 2: Generated Markdown

```markdown
# User Management API

**Version:** 1.0.0

## Authentication

All endpoints require Bearer token authentication.
```

Authorization: Bearer <token>

```

---

## Users

### List Users

```

GET /api/users

````

Returns a paginated list of users.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| limit | integer | No | 20 | Items per page |

**Response:** `200 OK`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
````

---

### Create User

```
POST /api/users
```

Create a new user account.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "name": "John Doe",
  "role": "user"
}
```

| Field | Type           | Required | Description                |
| ----- | -------------- | -------- | -------------------------- |
| email | string (email) | Yes      | User email address         |
| name  | string         | Yes      | Full name (2-100 chars)    |
| role  | enum           | No       | One of: admin, user, guest |

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newuser@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

---

### Get User

```
GET /api/users/{id}
```

Retrieve a user by their ID.

**Path Parameters:**

| Name | Type | Description |
| ---- | ---- | ----------- |
| id   | uuid | User ID     |

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Status | Description    |
| ------ | -------------- |
| 404    | User not found |

---

### Update User

```
PUT /api/users/{id}
```

Update user details.

**Request Body:**

```json
{
  "name": "Jane Doe",
  "role": "admin"
}
```

All fields are optional.

---

### Delete User

```
DELETE /api/users/{id}
```

Delete a user. **Requires admin role.**

**Response:** `204 No Content`

**Errors:**

| Status | Description         |
| ------ | ------------------- |
| 403    | Admin role required |
| 404    | User not found      |

---

## Errors

All errors follow this format:

```json
{
  "status": 400,
  "code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "email": ["Invalid email format"]
  }
}
```

````

---

## Example 3: cURL Examples

```bash
# List users
curl -X GET 'https://api.example.com/api/users?page=1&limit=20' \
  -H 'Authorization: Bearer <token>'

# Create user
curl -X POST 'https://api.example.com/api/users' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "newuser@example.com",
    "name": "John Doe",
    "role": "user"
  }'

# Get user
curl -X GET 'https://api.example.com/api/users/550e8400-e29b-41d4-a716-446655440000' \
  -H 'Authorization: Bearer <token>'

# Update user
curl -X PUT 'https://api.example.com/api/users/550e8400-e29b-41d4-a716-446655440000' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Jane Doe"
  }'

# Delete user
curl -X DELETE 'https://api.example.com/api/users/550e8400-e29b-41d4-a716-446655440000' \
  -H 'Authorization: Bearer <token>'
````

---

## Example 4: JavaScript Fetch Examples

```javascript
// List users
const users = await fetch("/api/users?page=1&limit=20", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
}).then((res) => res.json());

// Create user
const newUser = await fetch("/api/users", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "newuser@example.com",
    name: "John Doe",
    role: "user",
  }),
}).then((res) => res.json());

// Update user
const updatedUser = await fetch(`/api/users/${userId}`, {
  method: "PUT",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name: "Jane Doe",
  }),
}).then((res) => res.json());

// Delete user
await fetch(`/api/users/${userId}`, {
  method: "DELETE",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```
