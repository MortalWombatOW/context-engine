# How to Configure Your Project

To use ContextEngine with your project, you need to create a configuration file.

## Step 1: Create the Config File

Create a file named `.context-engine.yaml` in the root of your project directory.

## Step 2: Define Commands

Map the abstract commands (`check`, `test`, `build`, `run`) to your project's specific commands.

```yaml
commands:
  check: "ruff check ."
  test: "pytest"
  build: "echo 'No build needed'"
  run: "python main.py"
```

## Step 3: Define Documentation Paths

Tell ContextEngine where to find your key documentation files. Paths are relative to the project root.

```yaml
docs:
  rules: "docs/rules.md"
  tasks: "docs/tasks.md"
  log: "docs/work_log.md"
  readme: "README.md"
```

## Step 4: Configure Delegation (Optional)

You can configure the default model and timeout for subagents.

```yaml
delegation:
  default_model: "gemini-3-pro-preview"
  timeout: 300
```
