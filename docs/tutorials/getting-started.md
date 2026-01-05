# Getting Started with ContextEngine

In this tutorial, you will learn how to set up ContextEngine for a new project and act as a "human-in-the-loop" for an AI coding assistant.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- An MCP-compatible client (e.g., [Claude Desktop](https://claude.ai/download))

## Step 1: Install ContextEngine

Open your terminal and install the package:

```bash
pip install git+https://github.com/MortalWombatOW/context-engine.git
```

## Step 2: Initialize a Project

Navigate to your project folder (or create a new one):

```bash
mkdir my-new-project
cd my-new-project
```

Create a default configuration file:

```yaml
# .context-engine.yaml
commands:
  check: "echo 'No check command'"
  test: "echo 'No test command'"
```

## Step 3: Start the Server

If you are using Claude Desktop:

1.  Open your `claude_desktop_config.json`.
2.  Add the server configuration:
    ```json
    "context-engine": {
      "command": "context-engine",
      "args": ["--project", "/absolute/path/to/my-new-project"]
    }
    ```
3.  Restart Claude Desktop.

## Step 4: Your First Workflow

In your AI chat interface:

1.  Type `/start` to load the project context.
2.  The agent will read your project structure and rules.
3.  Type `/plan "Create a hello world script"` to plan your first task.

Congratulations! You are now using ContextEngine to structure your development workflow.
