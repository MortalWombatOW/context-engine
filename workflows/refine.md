---
description: Maintain documentation accuracy and improve agent performance through reflection. Run after /finish or when process friction is identified.
---

# Workflow: Refine

**Goal**: Maintain documentation accuracy and improve agent performance through reflection.

## Protocol Steps

1.  **Synchronization (The Map)**
    * Scan the source directory for structural changes.
    * Update `{{ docs.index }}`:
        * Add new files.
        * Remove deleted files.
        * Update descriptions if responsibilities changed.
    * Ensure `{{ docs.log }}` reflects all recent activity.

2.  **Retrospective (The Mirror)**
    * Review recent work in `{{ docs.log }}` and Chat History.
    * Identify **Friction** (e.g., "The agent keeps forgetting to import the prelude").
    * Identify **Drift** (e.g., "We are ignoring a coding standard rule").

3.  **Evolution (The Upgrade)**
    * Propose specific changes to:
        * **Rules**: `{{ docs.rules }}` (The Law/Operational Rules).
        * **Process**: Workflow templates.
        * **Documentation**: `{{ docs.index }}` or `{{ docs.readme }}`.
    * Explain *how* these changes prevent the friction identified in Step 2.

4.  **Implementation**
    * Upon user approval, apply the changes to the files.
    * Log the "Refinement" in `{{ docs.log }}`.

5.  **Handoff**
    * Wait for user input or remind them to run `/next-task` if appropriate.
