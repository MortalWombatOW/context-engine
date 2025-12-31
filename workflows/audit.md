---
description: Comprehensive code review to ensure technical quality and product alignment. Run after /forge.
---

# Workflow: Audit

**Goal**: Comprehensive code review to ensure technical quality and product alignment.

## Protocol Steps

1.  **Product & Context Alignment**
    * Does the implementation strictly match the active task in `{{ docs.tasks }}`?
    * Have changes been reflected in `{{ docs.log }}`?

2.  **Code Quality & Norms**
    * **Rule Compliance**: Verify compliance with `{{ docs.rules }}`.
    * **Warning Audit**: Run `{{ commands.check }}`. If any warnings exist:
        * Verify each warning was addressed via root cause analysis, not suppression.
        * Check for `#[allow(...)]` or `# noqa` attributes—these are red flags unless explicitly justified.
    * **No-Fallback Audit**: If this task involved replacing functionality:
        * Verify the old implementation is deleted or clearly marked for removal.
        * Verify the new implementation is what's being used, not a silent revert.

3.  **Architectural Integrity**
    * Verify against `{{ docs.rules }}`.
    * Are patterns followed consistently?
    * Are systems properly organized?

4.  **Invisible Knowledge Extraction**
    * Ask: "Did we make a decision here that isn't obvious?"
    * If yes, add a note to `{{ docs.rules }}`.

5.  **Handoff**
    * If **Failed**: Remind the user to run `/forge` to fix issues.
    * If **Passed**: Remind the user to run `/accept`.