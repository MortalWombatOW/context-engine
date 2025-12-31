---
description: Load the complete mental model of the project. Run at the start of a session.
---

# Workflow: Init

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

3.  **Handoff**
    * Remind the user to run `/next-task` to begin work, or `/architect` if the plan is empty.
