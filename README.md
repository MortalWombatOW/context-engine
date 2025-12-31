# ContextEngine

An MCP server providing workflows that promote human-engaged agentic coding.

## Overview

ContextEngine serves as a bridge between AI coding assistants and structured workflows that encourage meaningful human-AI collaboration. Instead of fully automated coding, it promotes a balanced approach where humans remain engaged in the decision-making process.

**Key Features:**
- 🔄 **8 Workflow Prompts** - Structured processes from planning to completion
- 📝 **Documentation Enforcement** - `log_progress` tool ensures work is documented as it happens
- ⚙️ **Project Configuration** - Adapts to any language/project via `.context-engine.yaml`
- 🔌 **MCP Protocol** - Works with any MCP-compatible client

## Installation

```bash
# Install from source
pip install git+https://github.com/MortalWombatOW/context-engine.git

# Or for development
git clone https://github.com/MortalWombatOW/context-engine.git
cd context-engine
pip install -e ".[dev]"
```

## Project Configuration

Create a `.context-engine.yaml` file in your project root:

```yaml
# .context-engine.yaml

commands:
  check: "cargo check"      # or: npm run lint, pytest, go build, etc.
  test: "cargo test"        # or: npm test, pytest -v, go test, etc.
  build: "cargo build"
  run: "cargo run"

docs:
  rules: "AGENT.md"         # Architectural constraints and coding standards
  tasks: "WORK_PLAN.md"     # Task list with [ ]/[/]/[x] status markers
  log: "WORK_LOG.md"        # Session chronicle (appended by log_progress)
  index: "INDEX.md"         # Codebase navigation map
  readme: "README.md"       # Project overview
```

## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "context-engine": {
      "command": "context-engine",
      "args": ["--project", "/path/to/your/project"]
    }
  }
}
```

### Other MCP Clients

```bash
context-engine --project /path/to/your/project
```

## Workflows

ContextEngine provides 8 workflow prompts that form a complete development cycle:

| Prompt | Description | When to Use |
|--------|-------------|-------------|
| `/init` | Load project mental model | Start of session |
| `/architect` | Convert requirements to tasks | Planning new features |
| `/next-task` | Identify next unit of work | After init or accept |
| `/forge` | Implement a single task | Active development |
| `/audit` | Code review for quality | After implementation |
| `/accept` | Mark complete and persist | After audit passes |
| `/collaborate` | Prepare handoff notes | End of session |
| `/refine` | Improve docs and process | Periodic maintenance |

### Workflow Cycle

```
/init → /architect → /next-task → /forge → /audit → /accept → /next-task...
                                      ↘︎           ↙︎
                                       (iterate)

/collaborate ← at any point (session handoff)
/refine ← periodic (process improvement)
```

## Documentation Enforcement

The `log_progress` tool ensures documentation happens during work, not after:

```python
# Called at checkpoints in workflows
log_progress(
    task_id="3.2.1",
    status="implementing",  # started | implementing | verified | blocked | complete
    summary="Added user authentication module"
)
```

This:
1. Appends timestamped entry to your work log
2. Optionally updates task status in your task list
3. Creates an auditable trail of progress

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check .

# Type check
mypy src/context_engine
```

## License

MIT
