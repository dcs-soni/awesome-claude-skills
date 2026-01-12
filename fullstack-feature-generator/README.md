# Full Stack Feature Generator

A Claude Code Skill for scaffolding complete full-stack features with database models, API routes, validation schemas, services, UI components, and tests - all following your project's existing patterns and conventions.

## What It Does

When you ask Claude to add a new feature, this skill:

1. **Analyzes** your project structure and conventions
2. **Designs** the data model with you
3. **Generates** all necessary files across the stack
4. **Follows** your existing patterns (naming, architecture, ORM)
5. **Verifies** the generated code compiles and passes tests

## Installation

Copy to your project:

```bash
cp -r fullstack-feature-generator /path/to/your-project/.claude/skills/
```

Or install globally:

```bash
cp -r fullstack-feature-generator ~/.claude/skills/
```

## Usage

### Example Prompts

```
"Add a blog posts feature with title, content, author, and published status"

"Create CRUD for user profiles with avatar, bio, and social links"

"Scaffold a comments feature that belongs to posts"

"Add an orders feature with items, total, and status"
```

### Generated Files

For a "blog posts" feature, the skill generates:

```
prisma/schema.prisma        # Model definition (appended)
src/schemas/blog-post.schema.ts   # Zod validation
src/services/blog-post.service.ts # Business logic
src/controllers/blog-post.controller.ts  # Request handlers
src/routes/blog-post.routes.ts    # Route definitions
tests/blog-post.test.ts           # API tests
```

## Workflow

The skill follows a 9-step workflow:

| Step | Action                                 |
| ---- | -------------------------------------- |
| 1    | Analyze project structure and patterns |
| 2    | Design data model with user            |
| 3    | Generate database layer                |
| 4    | Create API routes and handlers         |
| 5    | Build service layer                    |
| 6    | Generate UI components (if applicable) |
| 7    | Create tests                           |
| 8    | Wire up imports                        |
| 9    | Verify and document                    |

## Supported Frameworks

### API

- Express
- Fastify
- NestJS
- FastAPI
- Flask

### ORM

- Prisma
- Drizzle
- TypeORM
- SQLAlchemy

### UI

- React
- Next.js
- Vue

### Validation

- Zod
- Pydantic

## Scripts

| Script                | Purpose                      | Usage                                                                                      |
| --------------------- | ---------------------------- | ------------------------------------------------------------------------------------------ |
| `analyze_project.py`  | Detect frameworks & patterns | `python scripts/analyze_project.py .`                                                      |
| `scaffold_feature.py` | Generate feature files       | `python scripts/scaffold_feature.py . --name "posts" --fields "title:string,content:text"` |
| `verify_feature.py`   | Verify generated code        | `python scripts/verify_feature.py . --feature "posts"`                                     |

## Reference Files

| File                           | Description                      |
| ------------------------------ | -------------------------------- |
| [PATTERNS.md](./PATTERNS.md)   | Architecture and coding patterns |
| [TEMPLATES.md](./TEMPLATES.md) | Code templates for all layers    |

## Configuration

Create `.claude/feature-config.yaml` to customize:

```yaml
naming:
  style: camelCase # camelCase, snake_case, PascalCase

layers:
  database: true
  api: true
  service: true
  ui: true
  tests: true

frameworks:
  api: express
  orm: prisma
  ui: react
  test: vitest
```

## Best Practices

1. **Always analyze first** - Let the skill understand your project before generating
2. **Review the data model** - Approve the schema design before code generation
3. **Check existing features** - The skill uses them as templates
4. **Run verification** - Ensure generated code compiles and tests pass
5. **Add auth as needed** - The skill generates protected routes by default

## Requirements

- Python 3.7+ (for utility scripts)
- Node.js (for TypeScript projects)
- Claude Code installed

## License

MIT
