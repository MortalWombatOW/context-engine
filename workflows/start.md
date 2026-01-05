---
description: Load the complete mental model of the project. Run at the start of a session.
---

# Workflow: Start

**Goal**: Load the complete mental model of the project.

## Protocol Steps

1.  **Core Protocol Loading**
    * Read `{{ docs.rules }}` (The Single Source of Truth).
    ```markdown
    {{ read_to_text(docs.rules) }}
    ```

    * Read `{{ docs.index }}` (The Map).
    ```markdown
    {{ read_to_text(docs.index) }}
    ```

2.  **Product Context Loading**
    * Read `{{ docs.readme }}` (Project Overview).
    ```markdown
    {{ read_to_text(docs.readme) }}
    ```

    * Read `{{ docs.tasks }}` (Project Status).
    ```markdown
    {{ read_to_text(docs.tasks) }}
    ```

3.  **Operational Guidelines**
    *   **Workflow Tools describe ACTIONS**: When you call a workflow tool (e.g., `execute_task`), it returns a prompt/set of instructions. **IT DOES NOT DO THE WORK.**
    *   **YOUR Responsibility**: You must read the output of the workflow tool and **EXECUTE** the instructions contained within it.
    *   **Delegation**:
        *   If the task is atomic and well-defined, you must use `delegate=True` (and `high_complexity=True/False`) to have a subagent execute the instructions.
        *   If you do NOT delegate, YOU are responsible for performing every step described in the workflow output.
        *   Subagents are **stateless** and have **one turn**.
    *   **Custom Delegation**:
        *   Use the `call_tool("delegate", ...)` directly for ad-hoc tasks NOT covered by a workflow.
        *   **When to use**:
            *   Brainstorming/Ideation independent of current state.
            *   Reviewing/Critiquing a specific file (pass via `context_files`).
            *   Generating small, self-contained assets (e.g., a regex, a SQL query).
        *   Do NOT use this for multi-step changes to the codebase.

4.  **Available Workflows**
    *   **start**: Load project context (start of session)
    *   **plan**: Research and convert requirements to tasks (planning)
    *   **execute_task**: Select next task and implement it
    *   **review**: Code review (after implementation)
    *   **finish**: Mark complete and commit (after review)
    *   **summarize**: Prepare session handoff
    *   **refine**: Improve docs and process
    *   **delegate**: Spawn a subagent for a one-off task (custom delegation)

    **Typical Flow**:
    `init → execute_task → review → finish`

5.  **Handoff**
    * Remind the user to run `/execute-task` to begin work, or `/plan` if the plan is empty.
