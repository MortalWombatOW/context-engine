# Architecture

ContextEngine operates as a Model Context Protocol (MCP) server that connects to your AI client (like Claude Desktop or Gemini).

## High-Level Overview

```mermaid
graph LR
    User[User] <--> Client[MCP Client\n(e.g. Claude)]
    Client <--> Server[ContextEngine Server]
    Server <--> Project[Your Project Files]
```

1.  **User** interacts with the Client.
2.  **Client** requests tools and prompts from the Server.
3.  **Server** reads/writes to the Project based on the active workflow.

## Key Components

### The Server (`server.py`)
A `FastMCP` application that exposes:
*   **Tools**: Functions the agent can call (e.g., `log_progress`, `delegate`).
*   **Prompts**: Templates that guide the agent's behavior (e.g., `execute_task`).

### The Config (`.context-engine.yaml`)
A YAML file in your project root that adapts the engine to your specific needs (commands, file paths).

### Template Engine (`templates.py`)
Renders the markdown prompts dynamically, injecting project-specific context (like file lists or rule content) into the agent's instructions.
