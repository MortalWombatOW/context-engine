# Configuration Reference

The `.context-engine.yaml` file controls how ContextEngine interacts with your project.

## Schema

```yaml
commands:
  check: string  # Command to lint/check code
  test: string   # Command to run tests
  build: string  # Command to build the project
  run: string    # Command to run the application

docs:
  rules: string  # Path to architectural rules (default: AGENT.md)
  tasks: string  # Path to task list (default: WORK_PLAN.md)
  log: string    # Path to work log (default: WORK_LOG.md)
  index: string  # Path to codebase map (default: INDEX.md)
  readme: string # Path to project overview (default: README.md)

delegation:
  default_model: string # Model for subagents (default: gemini-3-pro-preview)
  timeout: integer      # Timeout in seconds (default: 300)
```
