# Architecture Reference

Quick reference for understanding common project architectures and their characteristics.

---

## Project Type Detection

### Node.js / JavaScript

**Indicators:**

- `package.json` present
- `node_modules/` directory
- `.js`, `.ts`, `.mjs`, `.cjs` files

**Key Files to Read:**

- `package.json` - Dependencies, scripts, project metadata
- `tsconfig.json` - TypeScript configuration
- `package-lock.json` / `pnpm-lock.yaml` - Locked dependencies

**Common Entry Points:**

- `src/index.ts` or `src/main.ts`
- `index.js` in root
- `bin/` for CLI tools
- Check `main` and `bin` fields in package.json

---

### Python

**Indicators:**

- `requirements.txt`, `pyproject.toml`, or `setup.py`
- `__init__.py` files
- `.py` files

**Key Files to Read:**

- `pyproject.toml` - Modern Python config
- `requirements.txt` - Dependencies
- `setup.py` / `setup.cfg` - Package config

**Common Entry Points:**

- `main.py`, `app.py`, `run.py`
- `__main__.py` in package
- `manage.py` for Django

---

### Go

**Indicators:**

- `go.mod` file
- `.go` files
- `cmd/` directory

**Key Files to Read:**

- `go.mod` - Module name and dependencies
- `go.sum` - Dependency checksums

**Common Entry Points:**

- `main.go` in root
- `cmd/<app>/main.go` for multiple binaries
- Look for `func main()`

---

### Rust

**Indicators:**

- `Cargo.toml` file
- `src/` with `.rs` files

**Key Files to Read:**

- `Cargo.toml` - Dependencies and metadata
- `Cargo.lock` - Locked versions

**Common Entry Points:**

- `src/main.rs` for binaries
- `src/lib.rs` for libraries

---

## Framework Detection

### Backend Frameworks

| Framework  | Detection Files               | Entry Pattern            |
| ---------- | ----------------------------- | ------------------------ |
| Express.js | `express` in deps             | `app.listen()`           |
| Fastify    | `fastify` in deps             | `fastify.listen()`       |
| NestJS     | `@nestjs/core`                | `main.ts` with bootstrap |
| Django     | `django` in deps, `manage.py` | `urls.py`, `views.py`    |
| Flask      | `flask` in deps               | `app = Flask(__name__)`  |
| FastAPI    | `fastapi` in deps             | `app = FastAPI()`        |
| Gin (Go)   | `github.com/gin-gonic/gin`    | `gin.Default()`          |
| Echo (Go)  | `github.com/labstack/echo`    | `echo.New()`             |

### Frontend Frameworks

| Framework | Detection Files  | Key Directories             |
| --------- | ---------------- | --------------------------- |
| React     | `react` in deps  | `components/`, `src/App`    |
| Next.js   | `next` in deps   | `app/` or `pages/`          |
| Vue       | `vue` in deps    | `components/`, `.vue` files |
| Nuxt      | `nuxt` in deps   | `pages/`, `layouts/`        |
| Angular   | `@angular/core`  | `src/app/`, `.component.ts` |
| Svelte    | `svelte` in deps | `.svelte` files             |

---

## Common Directory Structures

### REST API (Node.js/Express)

```
src/
├── config/          # Configuration
├── controllers/     # Route handlers
├── middleware/      # Express middleware
├── models/          # Database models
├── routes/          # Route definitions
├── services/        # Business logic
├── utils/           # Helpers
├── types/           # TypeScript types
└── index.ts         # Entry point
```

### Full-Stack (Next.js)

```
app/                 # App router pages
├── api/             # API routes
├── (auth)/          # Route groups
├── layout.tsx       # Root layout
└── page.tsx         # Home page
components/          # React components
lib/                 # Utilities
prisma/              # Database schema
public/              # Static assets
```

### Microservice

```
src/
├── domain/          # Business entities
├── application/     # Use cases
├── infrastructure/  # External integrations
│   ├── database/
│   ├── messaging/
│   └── http/
├── interfaces/      # Controllers, handlers
└── main.ts          # Bootstrap
```

### CLI Tool

```
src/
├── commands/        # Individual commands
├── utils/           # Shared utilities
├── config/          # Configuration
└── index.ts         # CLI entry with commander/yargs
bin/
└── cli.js           # Executable entry
```

---

## Database Patterns

### ORM Detection

| ORM        | Detection        | Schema Location                  |
| ---------- | ---------------- | -------------------------------- |
| Prisma     | `@prisma/client` | `prisma/schema.prisma`           |
| Drizzle    | `drizzle-orm`    | `drizzle/` or `src/db/schema.ts` |
| TypeORM    | `typeorm`        | Entities in `src/entities/`      |
| Sequelize  | `sequelize`      | `models/` directory              |
| Mongoose   | `mongoose`       | `models/` with schemas           |
| SQLAlchemy | `sqlalchemy`     | `models.py` or `models/`         |
| GORM       | `gorm.io/gorm`   | Struct tags                      |

### Migration Locations

- Prisma: `prisma/migrations/`
- Drizzle: `drizzle/` or configured path
- TypeORM: `src/migrations/`
- Django: `<app>/migrations/`
- Alembic: `alembic/versions/`

---

## Configuration Hierarchy

### Environment Variables

```
Priority (highest to lowest):
1. CLI arguments
2. Environment variables (.env)
3. Config files (config/*.json)
4. Default values in code
```

### Common Config Files

| File                  | Purpose               |
| --------------------- | --------------------- |
| `.env`                | Environment variables |
| `.env.local`          | Local overrides       |
| `.env.production`     | Production settings   |
| `config/default.json` | Base configuration    |
| `tsconfig.json`       | TypeScript settings   |
| `eslint.config.js`    | Linting rules         |
| `prettier.config.js`  | Formatting rules      |
| `jest.config.js`      | Test configuration    |
| `vite.config.ts`      | Build configuration   |

---

## Quick Analysis Checklist

When analyzing a new codebase:

1. **Identify Language** - Check file extensions and config files
2. **Find Package Manager** - npm, pnpm, pip, go mod, cargo
3. **Detect Framework** - Check dependencies
4. **Locate Entry Point** - main file, bin, scripts
5. **Map Directory Structure** - Understand organization
6. **Find Database** - ORM, migrations, schemas
7. **Check Tests** - Test framework and location
8. **Read Documentation** - README, docs/, CONTRIBUTING
9. **Review CI/CD** - .github/workflows, Jenkinsfile
10. **Check Deployment** - Dockerfile, k8s/, serverless
