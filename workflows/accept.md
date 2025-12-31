---
description: Officially mark work as complete and persist it. Run after /audit. Run before /next-task or /refine.
---

# Workflow: Accept

**Goal**: Officially mark work as complete and persist it.

## Protocol Steps

1.  **Final Verification**
    * Run `{{ commands.check }}` one last time to ensure a clean state.
    * If this task has a test requirement:
        1. Run: `{{ commands.test }}`
        2. If tests pass, verification passes
        3. If verification fails, **ABORT** and return to `/forge` to fix

2.  **Documentation**
    * Update task status in `{{ docs.tasks }}` to `[x]`.
    * **⚠️ CHECKPOINT**: Call `log_progress(task_id, "complete", "Task completed: <summary of what was done>")`

3.  **Persistence (Git)**
    * Stage all changes: `git add -A`
    * Commit with descriptive message referencing the task ID
    * Push to remote (if configured)

4.  **Handoff**
    * Notify the user: "Task Complete."
    * Remind the user to run `/next-task` to continue, or `/refine` if the session is ending.