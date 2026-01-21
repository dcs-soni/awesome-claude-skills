# Claude Skills Collection

A curated collection of custom [Claude Code Skills](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview) to enhance your development workflow.

## Skills

| Skill                                                        | Description                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------------ |
| [codebase-onboarding](./codebase-onboarding)                 | Understand unfamiliar codebases quickly with architecture analysis |
| [api-docs-generator](./api-docs-generator)                   | Generate OpenAPI specs and API documentation from code             |
| [fullstack-feature-generator](./fullstack-feature-generator) | Generate complete full-stack features with DB, API, and UI         |
| [incident-response-helper](./incident-response-helper)       | Accelerate production incident response with log analysis          |

## Installation

Copy any skill to your project's `.claude/skills/` directory:

```bash
# Clone the repo
git clone https://github.com/dcs-soni/awesome-claude-skills.git

# Copy a skill to your project
cp -r awesome-claude-skills/codebase-onboarding /path/to/your-project/.claude/skills/
```

Or install globally:

```bash
cp -r awesome-claude-skills/codebase-onboarding ~/.claude/skills/
```

## Usage

Once installed, Claude Code automatically uses skills when relevant. Just ask:

- _"Help me understand this codebase"_ → triggers `codebase-onboarding`
- _"Help me respond to this production incident"_ → triggers `incident-response-helper`

## What are Claude Skills?

Skills are modular packages that extend Claude with specialized expertise. They include:

- **Instructions** - Workflows and best practices
- **Scripts** - Utility tools Claude can execute
- **References** - Domain knowledge and patterns

📖 [Learn more about Skills](https://code.claude.com/docs/en/skills)

## Contributing

Want to add a new skill or suggest improvements? Please create an issue to discuss your ideas before submitting changes. This helps ensure alignment and avoids duplicate efforts.

## License

MIT
