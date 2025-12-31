---
description: Convert requirements into atomic tasks. Run after /init. Run before /forge.
---

# Workflow: Architect

**Goal**: Convert requirements into atomic tasks.

## Protocol Steps

1.  **Context Loading**
    * Ensure context from `/init` is active. If not, read `{{ docs.rules }}` and `{{ docs.index }}`.

2.  **Architectural Critique**
    * Analyze the request against `{{ docs.rules }}` (The Law).
    * Check for impacts on core architectural patterns.

3.  **Micro-Planning**
    * Draft a list of tasks.
    * **Constraint**: Each task must be approx. 1 file change or 1 system.

4.  **Verification Planning**
    * For each major feature, plan how to test it:
        * **What to test**: What conditions demonstrate the feature works?
        * **Expected output**: What proves it works?
    * Add verification subtasks to `{{ docs.tasks }}`:
        ```
        - [ ] Add logging to prove feature behavior
        - [ ] Run verification: `{{ commands.test }}`
        ```
    * **Constraint**: A feature is not complete until verification passes.

5.  **Plan Update**
    * Update `{{ docs.tasks }}` with the new tasks.
    * **Rule**: Only `/architect` may add new feature tasks. `/forge` may add subtasks for bug fixes.

6.  **Handoff**
    * Remind the user to run `/forge` on the first new task.