---
description: Research context and convert requirements into atomic tasks. Run after /start. Run before /execute-task.
---

# Workflow: Plan

**Goal**: Research context and convert requirements into atomic tasks.

## Protocol Steps

1.  **Context Loading**
    * Ensure context from `/start` is active. If not, read `/start`, `{{ docs.rules }}` and `{{ docs.index }}`.

2.  **Research & Discovery**
    * **Codebase Analysis**: Search the codebase to understand existing patterns, conventions, and related code.
    * **Identify Dependencies**: Map out which files, modules, or systems will be affected.
    * **Find Similar Implementations**: Look for existing code that solves similar problems—follow established patterns.
    * **Document Unknowns**: List any technical questions or ambiguities that need clarification.
    * **User Clarification**: If critical unknowns exist, ask the user before proceeding.

3.  **Architectural Critique**
    * Analyze the request against `{{ docs.rules }}` (The Law).
    * Check for impacts on core architectural patterns.
    * **Risk Assessment**: Identify potential breaking changes or high-risk modifications.

4.  **Micro-Planning**
    * Draft a list of tasks based on your research.
    * **Constraint**: Each task must be approx. 1 file change or 1 system.
    * **Order**: Sequence tasks by dependency (foundations first).

5.  **Verification Planning**
    * For each major feature, plan how to test it:
        * **What to test**: What conditions demonstrate the feature works?
        * **Expected output**: What proves it works?
    * Add verification subtasks to `{{ docs.tasks }}`:
        ```
        - [ ] Add logging to prove feature behavior
        - [ ] Run verification: `{{ commands.test }}`
        ```
    * **Constraint**: A feature is not complete until verification passes.

6.  **Plan Update**
    * Update `{{ docs.tasks }}` with the new tasks.
    * **Rule**: Only `/plan` may add new feature tasks. `/execute-task` may add subtasks for bug fixes.

7.  **Handoff**
    * **STOP**: Do NOT proceed directly to executing the plan.
    * Wait for the `/execute-task` workflow to be run.
    * Remind the user to run `/execute-task` on the first new task.