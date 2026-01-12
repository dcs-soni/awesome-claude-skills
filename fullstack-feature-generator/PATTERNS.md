# Project Patterns Reference

Patterns to detect and follow when generating features.

---

## Architecture Patterns

### Clean Architecture (Recommended)

```
src/
├── domain/           # Business entities (pure, no dependencies)
│   └── [feature]/
│       ├── entity.ts
│       └── repository.interface.ts
├── application/      # Use cases and business logic
│   └── [feature]/
│       └── service.ts
├── infrastructure/   # External concerns
│   ├── database/
│   └── http/
└── interfaces/       # Controllers, handlers
    └── [feature]/
        └── controller.ts
```

**Detection:** Look for `domain/`, `application/`, `infrastructure/` directories.

---

### MVC Pattern

```
src/
├── models/           # Data models
├── views/            # Templates or components
├── controllers/      # Request handlers
└── routes/           # Route definitions
```

**Detection:** Look for `models/`, `views/`, `controllers/` directories.

---

### Feature-Based (Modular)

```
src/
└── features/
    └── [feature]/
        ├── components/
        ├── hooks/
        ├── services/
        ├── types/
        └── index.ts
```

**Detection:** Look for `features/` or `modules/` directory.

---

## Naming Conventions

### Detect from Existing Code

| Pattern    | Example          | Common In             |
| ---------- | ---------------- | --------------------- |
| camelCase  | `getUserById`    | JavaScript/TypeScript |
| snake_case | `get_user_by_id` | Python, Ruby          |
| PascalCase | `GetUserById`    | Go, C#                |
| kebab-case | `get-user-by-id` | URLs, filenames       |

### File Naming

| Type       | camelCase         | PascalCase        | kebab-case        |
| ---------- | ----------------- | ----------------- | ----------------- |
| Components | -                 | `UserProfile.tsx` | -                 |
| Services   | `user.service.ts` | `UserService.ts`  | `user-service.ts` |
| Routes     | `user.routes.ts`  | -                 | `user-routes.ts`  |
| Tests      | `user.test.ts`    | -                 | `user.test.ts`    |

---

## ORM Patterns

### Repository Pattern

```typescript
// Interface
interface UserRepository {
  findById(id: string): Promise<User | null>;
  findAll(options: QueryOptions): Promise<User[]>;
  create(data: CreateUserDto): Promise<User>;
  update(id: string, data: UpdateUserDto): Promise<User>;
  delete(id: string): Promise<void>;
}

// Implementation
class PrismaUserRepository implements UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(id: string) {
    return this.prisma.user.findUnique({ where: { id } });
  }
  // ...
}
```

### Active Record Pattern

```typescript
// Entity manages its own persistence
class User extends Model {
  async save() {
    if (this.id) {
      return db.update("users", this.id, this.toJSON());
    }
    return db.insert("users", this.toJSON());
  }
}
```

---

## API Patterns

### RESTful Conventions

| Action         | Method | Route          | Response     |
| -------------- | ------ | -------------- | ------------ |
| List           | GET    | /resources     | 200 + array  |
| Get            | GET    | /resources/:id | 200 + object |
| Create         | POST   | /resources     | 201 + object |
| Update         | PUT    | /resources/:id | 200 + object |
| Partial Update | PATCH  | /resources/:id | 200 + object |
| Delete         | DELETE | /resources/:id | 204          |

### Error Response Pattern

```typescript
interface ApiError {
  status: number;
  code: string;
  message: string;
  details?: Record<string, string[]>;
}

// Example
{
  "status": 400,
  "code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "email": ["Invalid email format"],
    "password": ["Must be at least 8 characters"]
  }
}
```

### Pagination Pattern

```typescript
interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}
```

---

## Service Layer Patterns

### Dependency Injection

```typescript
// Service with injected dependencies
class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private userService: UserService,
    private emailService: EmailService
  ) {}

  async createOrder(userId: string, items: OrderItem[]) {
    const user = await this.userService.getById(userId);
    const order = await this.orderRepo.create({ userId, items });
    await this.emailService.sendOrderConfirmation(user.email, order);
    return order;
  }
}
```

### Transaction Pattern

```typescript
async function createOrderWithItems(data: CreateOrderData) {
  return db.transaction(async (tx) => {
    const order = await tx.insert(orders).values(data.order).returning();
    const items = await tx
      .insert(orderItems)
      .values(data.items.map((item) => ({ ...item, orderId: order.id })))
      .returning();
    return { ...order, items };
  });
}
```

---

## Validation Patterns

### Zod Schema

```typescript
import { z } from "zod";

export const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  password: z.string().min(8),
});

export const updateUserSchema = createUserSchema.partial();

export type CreateUserInput = z.infer<typeof createUserSchema>;
export type UpdateUserInput = z.infer<typeof updateUserSchema>;
```

### Pydantic Schema (Python)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
```

---

## Authentication Patterns

### JWT Middleware

```typescript
const authMiddleware = async (req, res, next) => {
  const token = req.headers.authorization?.replace("Bearer ", "");

  if (!token) {
    return res.status(401).json({ error: "No token provided" });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = payload;
    next();
  } catch {
    return res.status(401).json({ error: "Invalid token" });
  }
};
```

### Role-Based Access

```typescript
const requireRole = (...roles: string[]) => {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
  };
};

// Usage
router.delete("/:id", authMiddleware, requireRole("admin"), controller.delete);
```

---

## Test Patterns

### AAA Pattern (Arrange-Act-Assert)

```typescript
it("should create user with valid data", async () => {
  // Arrange
  const userData = { email: "test@example.com", name: "Test" };

  // Act
  const result = await userService.create(userData);

  // Assert
  expect(result).toHaveProperty("id");
  expect(result.email).toBe(userData.email);
});
```

### Factory Pattern for Test Data

```typescript
// tests/factories/user.factory.ts
export const createUserData = (overrides = {}) => ({
  email: `user-${Date.now()}@example.com`,
  name: "Test User",
  password: "password123",
  ...overrides,
});
```

---

## Quick Detection Checklist

When analyzing a project, check for:

- [ ] Directory structure → Architecture pattern
- [ ] Existing service files → Naming convention
- [ ] package.json/requirements.txt → Framework
- [ ] ORM config → Database pattern
- [ ] Auth middleware → Auth pattern
- [ ] Existing tests → Test pattern
- [ ] API responses → Response format
