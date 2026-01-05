---
description: Select the next task and implement it with high quality. Run after /start or /finish. Run before /review.
---

# Workflow: Execute Task

**Goal**: Select the next available task and implement it with high quality.

## Protocol Steps

### Phase 1: Task Selection

1.  **Task Selection**
    * Identify the next available task in `{{ docs.tasks }}`.
    * Criteria: Marked `[ ]`, dependencies are `[x]`.
    * **Constraint**: Strict numerical order within Epics. Do not skip.

2.  **State Transition**
    * Mark the selected task as in-progress `[/]` in `{{ docs.tasks }}`.

### Phase 2: Implementation

1.  **Strategy Formulation & Design**
    * **Scope Safety**: Check `{{ docs.tasks }}`. If the requirement is missing, **ABORT** and trigger `/architect`. Do not invent tasks.
    * **Rule Injection**: Read `{{ docs.rules }}`. Quote the specific section that applies to this task in your plan.
    * **Detailed Design**: List components/files to modify. Describe the proposed logic and structural changes.
    * **User Review**: Present this plan to the user. **STOP** and wait for user approval or feedback before implementation.

2.  **Implementation**
    * Generate the code.
    * **⚠️ CHECKPOINT**: Call `log_progress(task_id, "implementing", "Brief summary of changes made")`
    * **Constraint**: Describe current behavior only, not historical changes.

3.  **Verification**
    * Run `{{ commands.check }}`.
    * **Warning Resolution**: If warnings exist:
        * For unused variables: Determine intent—remove if truly unused, integrate if implementation is incomplete.
        * For dead code: Determine if caller is missing (fix it) or code is obsolete (delete it).
        * **NEVER** suppress warnings without understanding the root cause.
    * Verify the implementation meets the criteria in `{{ docs.tasks }}`.
    * **Requirement**: Zero warnings before proceeding to `/review`.
    * **⚠️ CHECKPOINT**: Call `log_progress(task_id, "verified", "Verification passed: <details>")`

4.  **Test Creation** (if task has verification requirement)
    * Add appropriate logging/tests that prove the feature works correctly.
    * Run: `{{ commands.test }}`
    * If verification fails, fix the implementation and repeat.

## Interrupt Protocol: Bug/Error Discovery

**Trigger**: User identifies a bug or error during implementation.

1.  **Documentation**
    *   Add a subtask to `{{ docs.tasks }}` (indented under the current task) describing the error.

2.  **Resolution**
    *   Diagnose and fix the issue immediately.

3.  **Verification**
    *   Ask the user: "Is this resolved?"
    *   **Wait** for confirmation.

4.  **Resumption**
    *   Mark the subtask as `[x]`.
    *   Resume the original task.

5.  **Handoff**
    * Remind the user to run `/review` to review the code.
