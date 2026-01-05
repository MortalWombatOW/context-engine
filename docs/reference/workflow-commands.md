# Workflow Commands

ContextEngine provides the following workflows to structure your development process.

| Prompt | Description | When to Use |
|--------|-------------|-------------|
| `/start` | Load project mental model | Start of session |
| `/plan` | Research and plan tasks | Planning new features |
| `/execute-task` | Select next task and implement | After start or finish |
| `/review` | Code review for quality | After implementation |
| `/finish` | Mark complete and persist | After review passes |
| `/summarize` | Prepare handoff notes | End of session |
| `/refine` | Improve docs and process | Periodic maintenance |
| `delegate` | Spawn subagent | Ad-hoc tasks, reviews |

## Usage Cycle

The typical flow moves from planning to execution to verification:

1.  **Start**: `/start`
2.  **Plan**: `/plan`
3.  **Work**: `/execute-task` (iterative)
4.  **Review**: `/review`
5.  **Finish**: `/finish`

## Delegation

ContextEngine supports delegating work to Gemini subagents to save time and reduce token usage for the main agent.

### Workflow Delegation
All workflow tools accept the following arguments to execute the standard workflow via a subagent.

*   `delegate` (bool): If `True`, spawns a subagent to execute the instructions defined by the workflow.
*   `high_complexity` (bool): 
    *   `True` → Uses `gemini-3-pro-preview` (Best for reasoning, planning, complex coding).
    *   `False` → Uses `gemini-3-flash-preview` (Best for routine tasks, simple edits).

**Example**:
```python
plan(delegate=True, high_complexity=True)
```

### Custom Delegation
Use the `delegate` tool directly for ad-hoc tasks that don't fit a standard workflow.

**When to use**:
*   Brainstorming or Ideation.
*   Code review of specific files (`context_files` argument).
*   generating small, isolated snippets (regex, SQL).

**Arguments**:
*   `prompt`: The instructions for the subagent.
*   `context_files`: List of files to read (e.g., `['src/utils.py']`).
*   `high_complexity`: Same model logic as above.

**Example**:
```python
delegate(
    prompt="Review this file for potential SQL injection vulnerabilities.",
    context_files=["src/db.py"],
    high_complexity=True
)
```
