# Orphan File Finder

Analyze dependency graph to find unused "dead code" source files.

## Installation

```bash
cp -r orphan-file-finder /path/to/project/.claude/skills/
```

## Usage

```bash
python scripts/find_orphans.py .
```

## Options

- `--format json`: Output JSON for CI/CD integration.
- `--ignore-patterns`: Glob patterns to skip (e.g., `tests/*,*.d.ts`).

## How it works

1. **Scans** directory for code files (`.js`, `.ts`, `.py`, etc.).
2. **Parses** unique imports from every file.
3. **Resolves** imports to absolute paths.
4. **Calculates** In-Degree for every file.
5. **Reports** files with In-Degree = 0 (and are not common entry points).

## Limitations

- Does not detect dynamic imports (e.g., `import(someVar)`).
- Does not parse `tsconfig.json` paths (assumes relative or package root imports).
- False positives possible for files used only by external configurations (Docker, CI).

## License

MIT
