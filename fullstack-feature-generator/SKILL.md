---
name: fullstack-feature-generator
description:
  Generate complete full-stack features with database models, API routes,
  UI components, and tests in one workflow. Use when user asks to add a feature,
  create CRUD operations, scaffold endpoints, or build complete functionality
  across frontend and backend.
---

# Full Stack Feature Generator

A comprehensive skill for scaffolding complete features across the entire stack - from database schema to UI components - following clean architecture principles and your project's conventions.

## Quick Start

When a user requests a new feature, follow this checklist:

```
Feature Generation Progress:
- [ ] Step 1: Analyze requirements and existing patterns
- [ ] Step 2: Design data model and schema
- [ ] Step 3: Generate database layer (model + migration)
- [ ] Step 4: Create API layer (routes + handlers + validation)
- [ ] Step 5: Build service layer (business logic)
- [ ] Step 6: Generate UI components (if applicable)
- [ ] Step 7: Create tests for all layers
- [ ] Step 8: Wire up imports and update indexes
- [ ] Step 9: Verify and document
```

---

## Workflow

### Step 1: Analyze Requirements and Existing Patterns

Before generating any code, understand the context:

```bash
python .claude/skills/fullstack-feature-generator/scripts/analyze_project.py .
```

**Gather:**

- [ ] Feature name and description from user
- [ ] Existing project structure (see [PATTERNS.md](PATTERNS.md))
- [ ] Current ORM/database setup
- [ ] API framework in use
- [ ] Frontend framework (if applicable)
- [ ] Existing naming conventions
- [ ] Authentication/authorization patterns

**Key Questions to Ask:**

1. What entities/data does this feature involve?
2. Who can access this feature? (auth requirements)
3. What CRUD operations are needed?
4. Does it need real-time updates?
5. Are there related features to integrate with?

---

### Step 2: Design Data Model

Create the data model design before any code generation.

**Output a schema proposal:**

```markdown
## Data Model: [FeatureName]

### Entities

#### [EntityName]

| Field | Type | Constraints | Description       |
| ----- | ---- | ----------- | ----------------- |
| id    | uuid | PK, auto    | Unique identifier |
| ...   | ...  | ...         | ...               |

### Relationships

- [Entity A] has many [Entity B]
- [Entity B] belongs to [Entity A]

### Indexes

- idx*[entity]*[field] on [field] (for frequent queries)
```

**Validation Questions:**

- Are field names consistent with project conventions?
- Are relationships properly defined?
- Are indexes appropriate for expected queries?

---

### Step 3: Generate Database Layer

Based on detected ORM, generate appropriate files:

#### For Prisma (Node.js)

```prisma
// Add to prisma/schema.prisma

model FeatureName {
  id        String   @id @default(cuid())
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Add fields based on design
}
```

**Then run:**

```bash
npx prisma migrate dev --name add_[feature_name]
npx prisma generate
```

#### For Drizzle (Node.js)

```typescript
// src/db/schema/[feature].ts
import { pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

export const featureName = pgTable("feature_name", {
  id: uuid("id").primaryKey().defaultRandom(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  // Add fields
});
```

#### For SQLAlchemy (Python)

```python
# src/models/feature_name.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.db.base import Base
import uuid
from datetime import datetime

class FeatureName(Base):
    __tablename__ = 'feature_name'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add fields
```

---

### Step 4: Create API Layer

Generate routes, handlers, and validation.

#### Route Structure

Follow RESTful conventions:

| Method | Route               | Handler | Description              |
| ------ | ------------------- | ------- | ------------------------ |
| GET    | /api/[features]     | list    | List all with pagination |
| GET    | /api/[features]/:id | getById | Get single by ID         |
| POST   | /api/[features]     | create  | Create new               |
| PUT    | /api/[features]/:id | update  | Update existing          |
| DELETE | /api/[features]/:id | delete  | Delete by ID             |

#### For Express/Node.js

```typescript
// src/routes/[feature].routes.ts
import { Router } from "express";
import { FeatureController } from "../controllers/[feature].controller";
import { validateRequest } from "../middleware/validate";
import {
  createFeatureSchema,
  updateFeatureSchema,
} from "../schemas/[feature].schema";

const router = Router();
const controller = new FeatureController();

router.get("/", controller.list);
router.get("/:id", controller.getById);
router.post("/", validateRequest(createFeatureSchema), controller.create);
router.put("/:id", validateRequest(updateFeatureSchema), controller.update);
router.delete("/:id", controller.delete);

export default router;
```

#### For FastAPI (Python)

```python
# src/routes/[feature].py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.[feature] import FeatureCreate, FeatureUpdate, FeatureResponse
from src.services.[feature]_service import FeatureService
from src.db.session import get_db

router = APIRouter(prefix="/[features]", tags=["[features]"])

@router.get("/", response_model=list[FeatureResponse])
async def list_features(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return FeatureService(db).list(skip=skip, limit=limit)

@router.get("/{id}", response_model=FeatureResponse)
async def get_feature(id: str, db: Session = Depends(get_db)):
    feature = FeatureService(db).get_by_id(id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@router.post("/", response_model=FeatureResponse, status_code=201)
async def create_feature(data: FeatureCreate, db: Session = Depends(get_db)):
    return FeatureService(db).create(data)

@router.put("/{id}", response_model=FeatureResponse)
async def update_feature(id: str, data: FeatureUpdate, db: Session = Depends(get_db)):
    return FeatureService(db).update(id, data)

@router.delete("/{id}", status_code=204)
async def delete_feature(id: str, db: Session = Depends(get_db)):
    FeatureService(db).delete(id)
```

---

### Step 5: Build Service Layer

Encapsulate business logic separately from routes.

```typescript
// src/services/[feature].service.ts
import { db } from "../db";
import { featureTable } from "../db/schema";
import { eq } from "drizzle-orm";
import {
  CreateFeatureInput,
  UpdateFeatureInput,
} from "../schemas/[feature].schema";

export class FeatureService {
  async list(options: { limit?: number; offset?: number } = {}) {
    const { limit = 50, offset = 0 } = options;
    return db.select().from(featureTable).limit(limit).offset(offset);
  }

  async getById(id: string) {
    const [result] = await db
      .select()
      .from(featureTable)
      .where(eq(featureTable.id, id));
    return result ?? null;
  }

  async create(data: CreateFeatureInput) {
    const [result] = await db.insert(featureTable).values(data).returning();
    return result;
  }

  async update(id: string, data: UpdateFeatureInput) {
    const [result] = await db
      .update(featureTable)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(featureTable.id, id))
      .returning();
    return result;
  }

  async delete(id: string) {
    await db.delete(featureTable).where(eq(featureTable.id, id));
  }
}
```

---

### Step 6: Generate UI Components (if applicable)

For frontend features, create components following project conventions.

#### React Component Structure

```
src/features/[feature-name]/
├── components/
│   ├── [Feature]List.tsx
│   ├── [Feature]Card.tsx
│   ├── [Feature]Form.tsx
│   └── [Feature]Detail.tsx
├── hooks/
│   └── use[Feature].ts
├── api/
│   └── [feature].api.ts
├── types/
│   └── [feature].types.ts
└── index.ts
```

See [TEMPLATES.md](TEMPLATES.md) for component templates.

---

### Step 7: Create Tests

Generate tests for each layer:

#### API Tests

```typescript
// tests/[feature].test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import request from "supertest";
import { app } from "../src/app";
import { db } from "../src/db";

describe("[Feature] API", () => {
  describe("POST /api/[features]", () => {
    it("should create a new [feature]", async () => {
      const response = await request(app)
        .post("/api/[features]")
        .send({ name: "Test Feature" })
        .expect(201);

      expect(response.body).toHaveProperty("id");
      expect(response.body.name).toBe("Test Feature");
    });

    it("should return 400 for invalid data", async () => {
      await request(app).post("/api/[features]").send({}).expect(400);
    });
  });

  describe("GET /api/[features]", () => {
    it("should return paginated list", async () => {
      const response = await request(app).get("/api/[features]").expect(200);

      expect(Array.isArray(response.body)).toBe(true);
    });
  });

  describe("GET /api/[features]/:id", () => {
    it("should return 404 for non-existent [feature]", async () => {
      await request(app).get("/api/[features]/non-existent-id").expect(404);
    });
  });
});
```

#### Service Tests

```typescript
// tests/services/[feature].service.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { FeatureService } from "../../src/services/[feature].service";

describe("FeatureService", () => {
  let service: FeatureService;

  beforeEach(() => {
    service = new FeatureService();
  });

  describe("create", () => {
    it("should create and return new feature", async () => {
      const result = await service.create({ name: "Test" });
      expect(result).toHaveProperty("id");
    });
  });
});
```

---

### Step 8: Wire Up Imports

Update index files and register routes:

```typescript
// src/routes/index.ts
import featureRoutes from "./[feature].routes";

// Add to router registration
app.use("/api/[features]", featureRoutes);
```

```typescript
// src/db/schema/index.ts
export * from "./[feature]";
```

---

### Step 9: Verify and Document

Run verification checks:

```bash
# Type check
npm run typecheck

# Run tests
npm test

# Lint
npm run lint
```

**Create feature documentation:**

```markdown
## [Feature Name]

### Overview

Brief description of what this feature does.

### API Endpoints

| Method | Endpoint        | Description |
| ------ | --------------- | ----------- |
| GET    | /api/[features] | List all    |
| POST   | /api/[features] | Create new  |
| ...    | ...             | ...         |

### Data Model

[Schema documentation]

### Usage Examples

[Code examples]
```

---

## Configuration

### Feature Configuration File

Create `.claude/feature-config.yaml` to customize generation:

```yaml
# Feature generation preferences
naming:
  style: camelCase # camelCase, snake_case, PascalCase
  plural: auto # auto-pluralize route names

layers:
  database: true
  api: true
  service: true
  ui: true
  tests: true

frameworks:
  api: express # express, fastify, fastapi, gin
  orm: prisma # prisma, drizzle, typeorm, sqlalchemy
  ui: react # react, vue, svelte, none
  test: vitest # vitest, jest, pytest

templates:
  useCustom: false
  path: .claude/templates/
```

---

## Examples

### Example 1: Blog Posts Feature

**User:** "Add a blog posts feature with title, content, author, and published status"

**Generated Files:**

```
prisma/schema.prisma (updated)
src/db/schema/posts.ts
src/routes/posts.routes.ts
src/controllers/posts.controller.ts
src/services/posts.service.ts
src/schemas/posts.schema.ts
tests/posts.test.ts
```

### Example 2: User Profiles Feature

**User:** "Create user profiles with avatar upload, bio, and social links"

**Generated Files:**

```
prisma/schema.prisma (updated)
src/db/schema/profiles.ts
src/routes/profiles.routes.ts
src/services/profiles.service.ts
src/services/upload.service.ts
src/features/profile/components/
tests/profiles.test.ts
```

---

## Anti-Patterns to Avoid

1. **Don't skip validation** - Always generate input validation schemas
2. **Don't mix concerns** - Keep routes thin, logic in services
3. **Don't forget auth** - Add auth middleware where needed
4. **Don't ignore errors** - Generate proper error handling
5. **Don't skip tests** - At minimum, generate happy path tests

---

## Related Skills

- **codebase-onboarding** - Understand project before generating
- **api-documentation** - Document generated endpoints
- **verification-layer** - Verify generated code works
