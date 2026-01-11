# Common Codebase Patterns

Reference guide for identifying architectural and coding patterns in codebases.

---

## Architectural Patterns

### MVC (Model-View-Controller)

**Indicators:**

- `models/`, `views/`, `controllers/` directories
- Clear separation between data, presentation, and logic
- Common in: Rails, Django, Laravel, Express

**Structure:**

```
app/
├── models/       # Data and business logic
├── views/        # Presentation templates
└── controllers/  # Request handling
```

---

### Clean Architecture / Hexagonal

**Indicators:**

- `domain/`, `application/`, `infrastructure/` layers
- Dependency injection usage
- Interfaces defined separately from implementations
- Common in: Enterprise Java, modern Node.js

**Structure:**

```
src/
├── domain/           # Business entities and rules
├── application/      # Use cases and services
├── infrastructure/   # External concerns (DB, HTTP)
└── interfaces/       # Controllers, CLI, etc.
```

---

### Microservices

**Indicators:**

- Multiple `package.json` or `go.mod` files
- Docker compose with multiple services
- API gateway patterns
- Service-to-service communication

**Structure:**

```
services/
├── user-service/
├── order-service/
├── payment-service/
└── api-gateway/
```

---

### Monorepo

**Indicators:**

- `packages/` or `apps/` directories
- Workspace configuration (pnpm, yarn, lerna, turborepo)
- Shared libraries between packages

**Structure:**

```
packages/
├── shared/           # Common utilities
├── ui/               # Component library
├── api/              # Backend service
└── web/              # Frontend app
```

---

## Code Organization Patterns

### Feature-Based Structure

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── index.ts
│   ├── dashboard/
│   └── settings/
```

### Layer-Based Structure

```
src/
├── components/
├── hooks/
├── services/
├── utils/
└── types/
```

---

## Error Handling Patterns

### Try-Catch with Custom Errors

```typescript
class AppError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
  }
}

// Usage
throw new AppError(404, "User not found");
```

### Result Pattern

```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function findUser(id: string): Result<User, NotFoundError> {
  // Returns success or error without throwing
}
```

### Error Middleware (Express)

```typescript
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.statusCode || 500).json({ error: err.message });
});
```

---

## Data Access Patterns

### Repository Pattern

```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}

class PostgresUserRepository implements UserRepository {
  // Implementation
}
```

### Active Record

```typescript
class User extends Model {
  static tableName = "users";

  async save() {
    // Instance saves itself
  }
}
```

### Data Mapper

```typescript
// Entity has no DB knowledge
class User {
  constructor(public id: string, public name: string) {}
}

// Mapper handles persistence
class UserMapper {
  toDatabase(user: User): DbRow {}
  fromDatabase(row: DbRow): User {}
}
```

---

## Testing Patterns

### AAA Pattern (Arrange-Act-Assert)

```typescript
test("should create user", () => {
  // Arrange
  const userData = { name: "Test" };

  // Act
  const user = createUser(userData);

  // Assert
  expect(user.name).toBe("Test");
});
```

### Test File Locations

**Co-located:**

```
src/
├── user.ts
└── user.test.ts
```

**Separate:**

```
src/user.ts
tests/user.test.ts
```

---

## Configuration Patterns

### Environment Variables

```typescript
// config/index.ts
export const config = {
  port: process.env.PORT || 3000,
  dbUrl: process.env.DATABASE_URL,
  jwtSecret: process.env.JWT_SECRET!,
};
```

### Configuration Files

```
config/
├── default.json
├── development.json
├── production.json
└── test.json
```

---

## API Patterns

### RESTful Routes

```
GET    /users          # List
POST   /users          # Create
GET    /users/:id      # Read
PUT    /users/:id      # Update
DELETE /users/:id      # Delete
```

### Controller Pattern

```typescript
class UserController {
  async index(req, res) {} // GET /users
  async show(req, res) {} // GET /users/:id
  async create(req, res) {} // POST /users
  async update(req, res) {} // PUT /users/:id
  async destroy(req, res) {} // DELETE /users/:id
}
```

---

## Dependency Injection Patterns

### Constructor Injection

```typescript
class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService
  ) {}
}
```

### Container Pattern

```typescript
const container = {
  userRepository: new PostgresUserRepository(),
  emailService: new SendGridEmailService(),
};

const userService = new UserService(
  container.userRepository,
  container.emailService
);
```

---

## Quick Pattern Detection

| Files Found                              | Likely Pattern      |
| ---------------------------------------- | ------------------- |
| `docker-compose.yml` + multiple services | Microservices       |
| `packages/` + workspace config           | Monorepo            |
| `domain/`, `application/`                | Clean Architecture  |
| `models/`, `views/`, `controllers/`      | MVC                 |
| `features/` with nested structure        | Feature-based       |
| `.env`, `.env.example`                   | Env-based config    |
| `prisma/`, `drizzle/`                    | ORM with migrations |
| `__tests__/` or `*.test.ts`              | Jest testing        |
