#!/usr/bin/env python3
"""
Generate feature scaffold based on detected project conventions.

Usage:
    python scaffold_feature.py <path> --name "blog posts" --fields "title:string,content:text,published:boolean"

Output:
    - List of files to create
    - Generated code for each file
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def to_pascal_case(text: str) -> str:
    """Convert to PascalCase."""
    words = re.split(r'[\s_-]+', text.lower())
    return ''.join(word.capitalize() for word in words)


def to_camel_case(text: str) -> str:
    """Convert to camelCase."""
    pascal = to_pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def to_snake_case(text: str) -> str:
    """Convert to snake_case."""
    words = re.split(r'[\s_-]+', text.lower())
    return '_'.join(words)


def to_kebab_case(text: str) -> str:
    """Convert to kebab-case."""
    words = re.split(r'[\s_-]+', text.lower())
    return '-'.join(words)


def pluralize(word: str) -> str:
    """Simple pluralization."""
    if word.endswith('y'):
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    else:
        return word + 's'


def parse_fields(fields_str: str) -> List[Dict]:
    """Parse field definitions like 'title:string,content:text,published:boolean'."""
    fields = []
    
    if not fields_str:
        return fields
    
    for field in fields_str.split(','):
        parts = field.strip().split(':')
        if len(parts) >= 2:
            field_name = parts[0].strip()
            field_type = parts[1].strip()
            nullable = len(parts) > 2 and 'optional' in parts[2].lower()
            
            fields.append({
                "name": field_name,
                "type": field_type,
                "nullable": nullable
            })
    
    return fields


def map_type_to_prisma(field_type: str) -> str:
    """Map generic type to Prisma type."""
    mapping = {
        "string": "String",
        "text": "String",
        "int": "Int",
        "integer": "Int",
        "float": "Float",
        "decimal": "Decimal",
        "boolean": "Boolean",
        "bool": "Boolean",
        "date": "DateTime",
        "datetime": "DateTime",
        "json": "Json",
        "uuid": "String",
    }
    return mapping.get(field_type.lower(), "String")


def map_type_to_typescript(field_type: str) -> str:
    """Map generic type to TypeScript type."""
    mapping = {
        "string": "string",
        "text": "string",
        "int": "number",
        "integer": "number",
        "float": "number",
        "decimal": "number",
        "boolean": "boolean",
        "bool": "boolean",
        "date": "Date",
        "datetime": "Date",
        "json": "Record<string, unknown>",
        "uuid": "string",
    }
    return mapping.get(field_type.lower(), "string")


def map_type_to_zod(field_type: str) -> str:
    """Map generic type to Zod validator."""
    mapping = {
        "string": "z.string()",
        "text": "z.string()",
        "int": "z.number().int()",
        "integer": "z.number().int()",
        "float": "z.number()",
        "decimal": "z.number()",
        "boolean": "z.boolean()",
        "bool": "z.boolean()",
        "date": "z.coerce.date()",
        "datetime": "z.coerce.date()",
        "json": "z.record(z.unknown())",
        "uuid": "z.string().uuid()",
    }
    return mapping.get(field_type.lower(), "z.string()")


def generate_prisma_model(name: str, fields: List[Dict]) -> str:
    """Generate Prisma model definition."""
    pascal = to_pascal_case(name)
    snake_plural = pluralize(to_snake_case(name))
    
    lines = [
        f"model {pascal} {{",
        "  id        String   @id @default(cuid())",
        "  createdAt DateTime @default(now()) @map(\"created_at\")",
        "  updatedAt DateTime @updatedAt @map(\"updated_at\")",
        "",
    ]
    
    for field in fields:
        prisma_type = map_type_to_prisma(field["type"])
        optional = "?" if field.get("nullable") else ""
        lines.append(f"  {to_camel_case(field['name'])} {prisma_type}{optional}")
    
    lines.extend([
        "",
        f"  @@map(\"{snake_plural}\")",
        "}",
    ])
    
    return "\n".join(lines)


def generate_zod_schema(name: str, fields: List[Dict]) -> str:
    """Generate Zod validation schema."""
    pascal = to_pascal_case(name)
    
    lines = [
        "import { z } from 'zod';",
        "",
        f"export const create{pascal}Schema = z.object({{",
        "  body: z.object({",
    ]
    
    for field in fields:
        zod_type = map_type_to_zod(field["type"])
        if field.get("nullable"):
            zod_type += ".optional()"
        lines.append(f"    {to_camel_case(field['name'])}: {zod_type},")
    
    lines.extend([
        "  }),",
        "});",
        "",
        f"export const update{pascal}Schema = z.object({{",
        f"  body: create{pascal}Schema.shape.body.partial(),",
        "  params: z.object({",
        "    id: z.string(),",
        "  }),",
        "});",
        "",
        f"export type Create{pascal}Input = z.infer<typeof create{pascal}Schema>['body'];",
        f"export type Update{pascal}Input = z.infer<typeof update{pascal}Schema>['body'];",
    ])
    
    return "\n".join(lines)


def generate_service(name: str, fields: List[Dict], orm: str = "prisma") -> str:
    """Generate service class."""
    pascal = to_pascal_case(name)
    camel = to_camel_case(name)
    camel_plural = pluralize(camel)
    
    if orm == "prisma":
        return f'''import {{ db }} from '../db';
import type {{ Create{pascal}Input, Update{pascal}Input }} from '../schemas/{to_kebab_case(name)}.schema';

export class {pascal}Service {{
  async list(options: {{ limit?: number; offset?: number }} = {{}}) {{
    const {{ limit = 20, offset = 0 }} = options;
    return db.{camel}.findMany({{
      take: limit,
      skip: offset,
      orderBy: {{ createdAt: 'desc' }},
    }});
  }}

  async getById(id: string) {{
    return db.{camel}.findUnique({{ where: {{ id }} }});
  }}

  async create(data: Create{pascal}Input) {{
    return db.{camel}.create({{ data }});
  }}

  async update(id: string, data: Update{pascal}Input) {{
    return db.{camel}.update({{
      where: {{ id }},
      data,
    }});
  }}

  async delete(id: string) {{
    return db.{camel}.delete({{ where: {{ id }} }});
  }}
}}
'''
    else:
        return f"// Service for {pascal} - implement based on your ORM"


def generate_controller(name: str) -> str:
    """Generate Express controller."""
    pascal = to_pascal_case(name)
    kebab = to_kebab_case(name)
    
    return f'''import {{ Request, Response, NextFunction }} from 'express';
import {{ {pascal}Service }} from '../services/{kebab}.service';
import {{ AppError }} from '../utils/errors';

export class {pascal}Controller {{
  private service: {pascal}Service;

  constructor() {{
    this.service = new {pascal}Service();
  }}

  list = async (req: Request, res: Response, next: NextFunction) => {{
    try {{
      const {{ page = 1, limit = 20 }} = req.query;
      const result = await this.service.list({{
        offset: (Number(page) - 1) * Number(limit),
        limit: Number(limit),
      }});
      res.json(result);
    }} catch (error) {{
      next(error);
    }}
  }};

  getById = async (req: Request, res: Response, next: NextFunction) => {{
    try {{
      const item = await this.service.getById(req.params.id);
      if (!item) throw new AppError(404, '{pascal} not found');
      res.json(item);
    }} catch (error) {{
      next(error);
    }}
  }};

  create = async (req: Request, res: Response, next: NextFunction) => {{
    try {{
      const item = await this.service.create(req.body);
      res.status(201).json(item);
    }} catch (error) {{
      next(error);
    }}
  }};

  update = async (req: Request, res: Response, next: NextFunction) => {{
    try {{
      const item = await this.service.update(req.params.id, req.body);
      if (!item) throw new AppError(404, '{pascal} not found');
      res.json(item);
    }} catch (error) {{
      next(error);
    }}
  }};

  delete = async (req: Request, res: Response, next: NextFunction) => {{
    try {{
      await this.service.delete(req.params.id);
      res.status(204).send();
    }} catch (error) {{
      next(error);
    }}
  }};
}}
'''


def generate_routes(name: str) -> str:
    """Generate Express routes."""
    pascal = to_pascal_case(name)
    kebab = to_kebab_case(name)
    
    return f'''import {{ Router }} from 'express';
import {{ {pascal}Controller }} from '../controllers/{kebab}.controller';
import {{ validateRequest }} from '../middleware/validate';
import {{ create{pascal}Schema, update{pascal}Schema }} from '../schemas/{kebab}.schema';

const router = Router();
const controller = new {pascal}Controller();

router.get('/', controller.list);
router.get('/:id', controller.getById);
router.post('/', validateRequest(create{pascal}Schema), controller.create);
router.put('/:id', validateRequest(update{pascal}Schema), controller.update);
router.delete('/:id', controller.delete);

export default router;
'''


def generate_test(name: str) -> str:
    """Generate API tests."""
    pascal = to_pascal_case(name)
    kebab = to_kebab_case(name)
    kebab_plural = pluralize(kebab)
    
    return f'''import {{ describe, it, expect, beforeEach, afterEach }} from 'vitest';
import request from 'supertest';
import {{ app }} from '../src/app';
import {{ db }} from '../src/db';

describe('{pascal} API', () => {{
  afterEach(async () => {{
    // Clean up test data
  }});

  describe('GET /api/{kebab_plural}', () => {{
    it('should return list', async () => {{
      const response = await request(app)
        .get('/api/{kebab_plural}')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
    }});
  }});

  describe('POST /api/{kebab_plural}', () => {{
    it('should create new {kebab}', async () => {{
      const response = await request(app)
        .post('/api/{kebab_plural}')
        .send({{ /* valid data */ }})
        .expect(201);

      expect(response.body).toHaveProperty('id');
    }});

    it('should return 400 for invalid data', async () => {{
      await request(app)
        .post('/api/{kebab_plural}')
        .send({{}})
        .expect(400);
    }});
  }});

  describe('GET /api/{kebab_plural}/:id', () => {{
    it('should return 404 for non-existent', async () => {{
      await request(app)
        .get('/api/{kebab_plural}/non-existent-id')
        .expect(404);
    }});
  }});
}});
'''


def generate_scaffold(name: str, fields: List[Dict], output_dir: Path = None) -> Dict:
    """Generate all scaffold files."""
    kebab = to_kebab_case(name)
    
    files = {
        f"prisma/schema.prisma.append": generate_prisma_model(name, fields),
        f"src/schemas/{kebab}.schema.ts": generate_zod_schema(name, fields),
        f"src/services/{kebab}.service.ts": generate_service(name, fields),
        f"src/controllers/{kebab}.controller.ts": generate_controller(name),
        f"src/routes/{kebab}.routes.ts": generate_routes(name),
        f"tests/{kebab}.test.ts": generate_test(name),
    }
    
    return files


def main():
    if len(sys.argv) < 2:
        print("Usage: python scaffold_feature.py <path> --name <feature> --fields <field:type,...>")
        sys.exit(1)
    
    root = Path(sys.argv[1]).resolve()
    
    # Parse arguments
    name = "example"
    fields_str = ""
    
    if "--name" in sys.argv:
        idx = sys.argv.index("--name")
        if idx + 1 < len(sys.argv):
            name = sys.argv[idx + 1]
    
    if "--fields" in sys.argv:
        idx = sys.argv.index("--fields")
        if idx + 1 < len(sys.argv):
            fields_str = sys.argv[idx + 1]
    
    fields = parse_fields(fields_str)
    files = generate_scaffold(name, fields)
    
    print("=" * 60)
    print(f"SCAFFOLD: {to_pascal_case(name)}")
    print("=" * 60)
    
    for filepath, content in files.items():
        print(f"\n📄 {filepath}")
        print("-" * 40)
        print(content[:500] + "..." if len(content) > 500 else content)
    
    if "--json" in sys.argv:
        print(json.dumps(files, indent=2))


if __name__ == "__main__":
    main()
