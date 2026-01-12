# Code Templates

Ready-to-use templates for common feature components.

---

## Database Layer Templates

### Prisma Model Template

```prisma
model {{PascalCase}} {
  id        String   @id @default(cuid())
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  // Core fields
  {{#fields}}
  {{name}} {{type}} {{constraints}}
  {{/fields}}

  // Relations
  {{#relations}}
  {{name}} {{relatedModel}}{{relationModifier}} @relation({{relationArgs}})
  {{/relations}}

  @@map("{{snake_case_plural}}")
}
```

### Drizzle Schema Template

```typescript
// src/db/schema/{{kebab-case}}.ts
import { pgTable, text, timestamp, uuid, varchar, boolean } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const {{camelCasePlural}} = pgTable('{{snake_case_plural}}', {
  id: uuid('id').primaryKey().defaultRandom(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),

  // Add your fields here
});

export const {{camelCasePlural}}Relations = relations({{camelCasePlural}}, ({ one, many }) => ({
  // Define relations here
}));

export type {{PascalCase}} = typeof {{camelCasePlural}}.$inferSelect;
export type New{{PascalCase}} = typeof {{camelCasePlural}}.$inferInsert;
```

---

## API Layer Templates

### Express Controller Template

```typescript
// src/controllers/{{kebab-case}}.controller.ts
import { Request, Response, NextFunction } from 'express';
import { {{PascalCase}}Service } from '../services/{{kebab-case}}.service';
import { AppError } from '../utils/errors';

export class {{PascalCase}}Controller {
  private service: {{PascalCase}}Service;

  constructor() {
    this.service = new {{PascalCase}}Service();
  }

  list = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { page = 1, limit = 20 } = req.query;
      const result = await this.service.list({
        offset: (Number(page) - 1) * Number(limit),
        limit: Number(limit),
      });
      res.json(result);
    } catch (error) {
      next(error);
    }
  };

  getById = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { id } = req.params;
      const item = await this.service.getById(id);

      if (!item) {
        throw new AppError(404, '{{PascalCase}} not found');
      }

      res.json(item);
    } catch (error) {
      next(error);
    }
  };

  create = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const item = await this.service.create(req.body);
      res.status(201).json(item);
    } catch (error) {
      next(error);
    }
  };

  update = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { id } = req.params;
      const item = await this.service.update(id, req.body);

      if (!item) {
        throw new AppError(404, '{{PascalCase}} not found');
      }

      res.json(item);
    } catch (error) {
      next(error);
    }
  };

  delete = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { id } = req.params;
      await this.service.delete(id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  };
}
```

### Express Routes Template

```typescript
// src/routes/{{kebab-case}}.routes.ts
import { Router } from 'express';
import { {{PascalCase}}Controller } from '../controllers/{{kebab-case}}.controller';
import { validateRequest } from '../middleware/validate';
import { create{{PascalCase}}Schema, update{{PascalCase}}Schema } from '../schemas/{{kebab-case}}.schema';
import { authenticate } from '../middleware/auth';

const router = Router();
const controller = new {{PascalCase}}Controller();

// Public routes
router.get('/', controller.list);
router.get('/:id', controller.getById);

// Protected routes
router.post('/', authenticate, validateRequest(create{{PascalCase}}Schema), controller.create);
router.put('/:id', authenticate, validateRequest(update{{PascalCase}}Schema), controller.update);
router.delete('/:id', authenticate, controller.delete);

export default router;
```

### FastAPI Router Template

```python
# src/routes/{{snake_case}}.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from src.schemas.{{snake_case}} import (
    {{PascalCase}}Create,
    {{PascalCase}}Update,
    {{PascalCase}}Response,
    {{PascalCase}}ListResponse,
)
from src.services.{{snake_case}}_service import {{PascalCase}}Service
from src.db.session import get_db
from src.middleware.auth import get_current_user

router = APIRouter(prefix="/{{kebab-case-plural}}", tags=["{{PascalCase}}"])


@router.get("/", response_model={{PascalCase}}ListResponse)
async def list_{{snake_case_plural}}(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all {{snake_case_plural}} with pagination."""
    service = {{PascalCase}}Service(db)
    return service.list(skip=(page - 1) * limit, limit=limit)


@router.get("/{id}", response_model={{PascalCase}}Response)
async def get_{{snake_case}}(id: str, db: Session = Depends(get_db)):
    """Get a single {{snake_case}} by ID."""
    service = {{PascalCase}}Service(db)
    item = service.get_by_id(id)
    if not item:
        raise HTTPException(status_code=404, detail="{{PascalCase}} not found")
    return item


@router.post("/", response_model={{PascalCase}}Response, status_code=201)
async def create_{{snake_case}}(
    data: {{PascalCase}}Create,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create a new {{snake_case}}."""
    service = {{PascalCase}}Service(db)
    return service.create(data, user_id=current_user.id)


@router.put("/{id}", response_model={{PascalCase}}Response)
async def update_{{snake_case}}(
    id: str,
    data: {{PascalCase}}Update,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Update an existing {{snake_case}}."""
    service = {{PascalCase}}Service(db)
    return service.update(id, data)


@router.delete("/{id}", status_code=204)
async def delete_{{snake_case}}(
    id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Delete a {{snake_case}}."""
    service = {{PascalCase}}Service(db)
    service.delete(id)
```

---

## Service Layer Templates

### TypeScript Service Template

```typescript
// src/services/{{kebab-case}}.service.ts
import { db } from '../db';
import { {{camelCasePlural}} } from '../db/schema';
import { eq, desc } from 'drizzle-orm';
import type { Create{{PascalCase}}Input, Update{{PascalCase}}Input } from '../schemas/{{kebab-case}}.schema';
import { AppError } from '../utils/errors';

export class {{PascalCase}}Service {
  async list(options: { limit?: number; offset?: number } = {}) {
    const { limit = 20, offset = 0 } = options;

    const items = await db
      .select()
      .from({{camelCasePlural}})
      .orderBy(desc({{camelCasePlural}}.createdAt))
      .limit(limit)
      .offset(offset);

    return items;
  }

  async getById(id: string) {
    const [item] = await db
      .select()
      .from({{camelCasePlural}})
      .where(eq({{camelCasePlural}}.id, id));

    return item ?? null;
  }

  async create(data: Create{{PascalCase}}Input) {
    const [item] = await db
      .insert({{camelCasePlural}})
      .values(data)
      .returning();

    return item;
  }

  async update(id: string, data: Update{{PascalCase}}Input) {
    const existing = await this.getById(id);

    if (!existing) {
      throw new AppError(404, '{{PascalCase}} not found');
    }

    const [item] = await db
      .update({{camelCasePlural}})
      .set({ ...data, updatedAt: new Date() })
      .where(eq({{camelCasePlural}}.id, id))
      .returning();

    return item;
  }

  async delete(id: string) {
    const existing = await this.getById(id);

    if (!existing) {
      throw new AppError(404, '{{PascalCase}} not found');
    }

    await db
      .delete({{camelCasePlural}})
      .where(eq({{camelCasePlural}}.id, id));
  }
}
```

### Python Service Template

```python
# src/services/{{snake_case}}_service.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from uuid import UUID

from src.models.{{snake_case}} import {{PascalCase}}
from src.schemas.{{snake_case}} import {{PascalCase}}Create, {{PascalCase}}Update


class {{PascalCase}}Service:
    def __init__(self, db: Session):
        self.db = db

    def list(self, skip: int = 0, limit: int = 20) -> List[{{PascalCase}}]:
        return (
            self.db.query({{PascalCase}})
            .order_by(desc({{PascalCase}}.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, id: str) -> Optional[{{PascalCase}}]:
        return self.db.query({{PascalCase}}).filter({{PascalCase}}.id == id).first()

    def create(self, data: {{PascalCase}}Create, user_id: Optional[str] = None) -> {{PascalCase}}:
        item = {{PascalCase}}(**data.model_dump())
        if user_id:
            item.created_by = user_id
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, id: str, data: {{PascalCase}}Update) -> Optional[{{PascalCase}}]:
        item = self.get_by_id(id)
        if not item:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, id: str) -> bool:
        item = self.get_by_id(id)
        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True
```

---

## Validation Schema Templates

### Zod Schema Template

```typescript
// src/schemas/{{kebab-case}}.schema.ts
import { z } from 'zod';

export const create{{PascalCase}}Schema = z.object({
  body: z.object({
    // Add required fields
    name: z.string().min(1).max(255),
    description: z.string().optional(),
    // Add more fields as needed
  }),
});

export const update{{PascalCase}}Schema = z.object({
  body: create{{PascalCase}}Schema.shape.body.partial(),
  params: z.object({
    id: z.string().uuid(),
  }),
});

export type Create{{PascalCase}}Input = z.infer<typeof create{{PascalCase}}Schema>['body'];
export type Update{{PascalCase}}Input = z.infer<typeof update{{PascalCase}}Schema>['body'];
```

### Pydantic Schema Template

```python
# src/schemas/{{snake_case}}.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class {{PascalCase}}Base(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class {{PascalCase}}Create({{PascalCase}}Base):
    pass


class {{PascalCase}}Update(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class {{PascalCase}}Response({{PascalCase}}Base):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class {{PascalCase}}ListResponse(BaseModel):
    data: List[{{PascalCase}}Response]
    total: int
    page: int
    limit: int
```

---

## React Component Templates

### List Component Template

```tsx
// src/features/{{kebab-case}}/components/{{PascalCase}}List.tsx
import { use{{PascalCase}}List } from '../hooks/use{{PascalCase}}';
import { {{PascalCase}}Card } from './{{PascalCase}}Card';
import { Loader, EmptyState } from '@/components/ui';

export function {{PascalCase}}List() {
  const { data, isLoading, error } = use{{PascalCase}}List();

  if (isLoading) {
    return <Loader />;
  }

  if (error) {
    return <div className="text-red-500">Error: {error.message}</div>;
  }

  if (!data?.length) {
    return <EmptyState message="No {{camelCasePlural}} found" />;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {data.map((item) => (
        <{{PascalCase}}Card key={item.id} item={item} />
      ))}
    </div>
  );
}
```

### Form Component Template

```tsx
// src/features/{{kebab-case}}/components/{{PascalCase}}Form.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { create{{PascalCase}}Schema, type Create{{PascalCase}}Input } from '../schemas';
import { useCreate{{PascalCase}} } from '../hooks/use{{PascalCase}}';
import { Button, Input, Form } from '@/components/ui';

interface {{PascalCase}}FormProps {
  onSuccess?: () => void;
  initialData?: Partial<Create{{PascalCase}}Input>;
}

export function {{PascalCase}}Form({ onSuccess, initialData }: {{PascalCase}}FormProps) {
  const { mutate, isPending } = useCreate{{PascalCase}}();

  const form = useForm<Create{{PascalCase}}Input>({
    resolver: zodResolver(create{{PascalCase}}Schema),
    defaultValues: initialData,
  });

  const onSubmit = (data: Create{{PascalCase}}Input) => {
    mutate(data, {
      onSuccess: () => {
        form.reset();
        onSuccess?.();
      },
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Name"
          {...form.register('name')}
          error={form.formState.errors.name?.message}
        />

        <Input
          label="Description"
          {...form.register('description')}
          error={form.formState.errors.description?.message}
        />

        <Button type="submit" loading={isPending}>
          Create {{PascalCase}}
        </Button>
      </form>
    </Form>
  );
}
```

### Hook Template

```tsx
// src/features/{{kebab-case}}/hooks/use{{PascalCase}}.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { {{camelCase}}Api } from '../api/{{kebab-case}}.api';
import type { Create{{PascalCase}}Input, Update{{PascalCase}}Input } from '../schemas';

const QUERY_KEY = ['{{camelCasePlural}}'];

export function use{{PascalCase}}List() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: {{camelCase}}Api.list,
  });
}

export function use{{PascalCase}}(id: string) {
  return useQuery({
    queryKey: [...QUERY_KEY, id],
    queryFn: () => {{camelCase}}Api.getById(id),
    enabled: !!id,
  });
}

export function useCreate{{PascalCase}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Create{{PascalCase}}Input) => {{camelCase}}Api.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useUpdate{{PascalCase}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Update{{PascalCase}}Input }) =>
      {{camelCase}}Api.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useDelete{{PascalCase}}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => {{camelCase}}Api.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}
```

---

## Test Templates

### API Test Template

```typescript
// tests/{{kebab-case}}.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import request from 'supertest';
import { app } from '../src/app';
import { db } from '../src/db';
import { {{camelCasePlural}} } from '../src/db/schema';
import { createTestUser, createAuthToken } from './helpers';

describe('{{PascalCase}} API', () => {
  let authToken: string;

  beforeEach(async () => {
    const user = await createTestUser();
    authToken = createAuthToken(user);
  });

  afterEach(async () => {
    await db.delete({{camelCasePlural}});
  });

  describe('GET /api/{{kebab-case-plural}}', () => {
    it('should return empty array when no {{camelCasePlural}} exist', async () => {
      const response = await request(app)
        .get('/api/{{kebab-case-plural}}')
        .expect(200);

      expect(response.body).toEqual([]);
    });

    it('should return paginated list', async () => {
      // Create test data
      await db.insert({{camelCasePlural}}).values([
        { name: 'Item 1' },
        { name: 'Item 2' },
      ]);

      const response = await request(app)
        .get('/api/{{kebab-case-plural}}?page=1&limit=10')
        .expect(200);

      expect(response.body).toHaveLength(2);
    });
  });

  describe('POST /api/{{kebab-case-plural}}', () => {
    it('should create new {{camelCase}} with valid data', async () => {
      const response = await request(app)
        .post('/api/{{kebab-case-plural}}')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'New Item' })
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe('New Item');
    });

    it('should return 400 for invalid data', async () => {
      await request(app)
        .post('/api/{{kebab-case-plural}}')
        .set('Authorization', `Bearer ${authToken}`)
        .send({})
        .expect(400);
    });

    it('should return 401 without auth token', async () => {
      await request(app)
        .post('/api/{{kebab-case-plural}}')
        .send({ name: 'New Item' })
        .expect(401);
    });
  });

  describe('GET /api/{{kebab-case-plural}}/:id', () => {
    it('should return {{camelCase}} by id', async () => {
      const [created] = await db
        .insert({{camelCasePlural}})
        .values({ name: 'Test Item' })
        .returning();

      const response = await request(app)
        .get(`/api/{{kebab-case-plural}}/${created.id}`)
        .expect(200);

      expect(response.body.id).toBe(created.id);
    });

    it('should return 404 for non-existent id', async () => {
      await request(app)
        .get('/api/{{kebab-case-plural}}/non-existent-id')
        .expect(404);
    });
  });

  describe('PUT /api/{{kebab-case-plural}}/:id', () => {
    it('should update existing {{camelCase}}', async () => {
      const [created] = await db
        .insert({{camelCasePlural}})
        .values({ name: 'Original' })
        .returning();

      const response = await request(app)
        .put(`/api/{{kebab-case-plural}}/${created.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Updated' })
        .expect(200);

      expect(response.body.name).toBe('Updated');
    });
  });

  describe('DELETE /api/{{kebab-case-plural}}/:id', () => {
    it('should delete existing {{camelCase}}', async () => {
      const [created] = await db
        .insert({{camelCasePlural}})
        .values({ name: 'To Delete' })
        .returning();

      await request(app)
        .delete(`/api/{{kebab-case-plural}}/${created.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(204);

      const found = await db.select().from({{camelCasePlural}}).where(eq({{camelCasePlural}}.id, created.id));
      expect(found).toHaveLength(0);
    });
  });
});
```

---

## Template Variables Reference

| Variable                | Example Input | Output     |
| ----------------------- | ------------- | ---------- |
| `{{PascalCase}}`        | blog post     | BlogPost   |
| `{{camelCase}}`         | blog post     | blogPost   |
| `{{camelCasePlural}}`   | blog post     | blogPosts  |
| `{{snake_case}}`        | blog post     | blog_post  |
| `{{snake_case_plural}}` | blog post     | blog_posts |
| `{{kebab-case}}`        | blog post     | blog-post  |
| `{{kebab-case-plural}}` | blog post     | blog-posts |
| `{{SCREAMING_CASE}}`    | blog post     | BLOG_POST  |
