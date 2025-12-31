"""MCP Server for ContextEngine workflows."""

from fastmcp.tools.tool import ToolResult
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastmcp import FastMCP

from .config import ContextEngineConfig, load_config, set_config, get_config
from .templates import render_workflow, list_workflows

# Create the FastMCP server instance
mcp = FastMCP(
    "ContextEngine",
    instructions="An MCP server for workflows that promote human-engaged agentic coding",
)


# =============================================================================
# Workflow Tools - Rendered templates accessible as tools
# =============================================================================

@mcp.tool()
def workflow_init() -> ToolResult:
    """Load the complete mental model of the project.
    
    Run at the start of a session before beginning work.
    Reads project rules, index, readme, and task list.
    """
    return ToolResult(content=render_workflow("init"))


@mcp.tool()
def workflow_architect(requirement: str | None = None) -> str:
    """Convert requirements into atomic tasks.
    
    Run when planning new work. Analyzes the request against project rules
    and creates a micro-plan of tasks.
    
    Args:
        requirement: Optional description of the feature/change to architect.
    """
    content = render_workflow("architect")
    if requirement:
        content = f"# Requirement\n\n{requirement}\n\n---\n\n{content}"
    return content


@mcp.tool()
def workflow_next_task() -> str:
    """Identify and lock the next unit of work.
    
    Run after init or accept to find what to work on next.
    Selects the next available task and marks it in-progress.
    """
    return render_workflow("next-task")


@mcp.tool()
def workflow_forge(task_id: str | None = None) -> str:
    """Implement a single atomic task with high quality.
    
    Run after next_task to begin implementation.
    Includes checkpoints for documentation via log_progress.
    
    Args:
        task_id: Optional specific task ID to implement.
    """
    content = render_workflow("forge")
    if task_id:
        content = f"# Active Task: {task_id}\n\n---\n\n{content}"
    return content


@mcp.tool()
def workflow_audit() -> str:
    """Comprehensive code review to ensure quality.
    
    Run after forge to review implemented changes.
    Checks code quality, architectural alignment, and documentation.
    """
    return render_workflow("audit")


@mcp.tool()
def workflow_accept() -> str:
    """Mark work complete and persist changes.
    
    Run after audit passes to finalize the task.
    Updates task status, logs completion, and commits changes.
    """
    return render_workflow("accept")


@mcp.tool()
def workflow_collaborate() -> str:
    """Prepare handoff for next agent session.
    
    Run when ending a session or hitting a complex blocker.
    Creates a handoff note with current state and next steps.
    """
    return render_workflow("collaborate")


@mcp.tool()
def workflow_refine() -> str:
    """Maintain documentation and improve process.
    
    Run periodically to sync documentation with code changes
    and identify process improvements.
    """
    return render_workflow("refine")


@mcp.tool()
def list_available_workflows() -> str:
    """List all available workflow tools.
    
    Returns descriptions of each workflow and when to use them.
    """
    workflows = {
        "workflow_init": "Load project context (start of session)",
        "workflow_architect": "Convert requirements to tasks (planning)",
        "workflow_next_task": "Find next task to work on",
        "workflow_forge": "Implement a task (active development)",
        "workflow_audit": "Code review (after implementation)",
        "workflow_accept": "Mark complete and commit (after audit)",
        "workflow_collaborate": "Prepare session handoff",
        "workflow_refine": "Improve docs and process",
    }
    
    lines = ["# Available Workflows\n"]
    for name, desc in workflows.items():
        lines.append(f"- **{name}**: {desc}")
    
    lines.append("\n## Typical Flow")
    lines.append("```")
    lines.append("workflow_init → workflow_next_task → workflow_forge → workflow_audit → workflow_accept")
    lines.append("```")
    
    return "\n".join(lines)


# =============================================================================
# Documentation Tool - Progress logging
# =============================================================================

@mcp.tool()
def log_progress(
    task_id: str,
    status: Literal["started", "implementing", "verified", "blocked", "complete"],
    summary: str,
) -> str:
    """Log progress checkpoint during task execution.
    
    Workflows instruct you to call this at specific checkpoints to ensure
    documentation happens during work, not after. This appends to the work
    log and can update task status.
    
    Args:
        task_id: The task identifier (e.g., "3.2.1", "Epic 4.2").
        status: Current status of the task.
        summary: Brief description of progress or changes made.
    
    Returns:
        Confirmation message.
    """
    config = get_config()
    log_path = config.get_doc_path("log")
    
    # Format the log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    status_emoji = {
        "started": "🚀",
        "implementing": "🔨", 
        "verified": "✅",
        "blocked": "🚧",
        "complete": "✓",
    }.get(status, "•")
    
    entry = f"\n**[{timestamp}]** {status_emoji} `{task_id}` ({status}): {summary}\n"
    
    # Append to work log
    try:
        if log_path.exists():
            with open(log_path, "a") as f:
                f.write(entry)
        else:
            # Create with header if doesn't exist
            with open(log_path, "w") as f:
                f.write(f"# Work Log\n{entry}")
        
        # Optionally update task status in work plan
        if status in ("started", "complete", "blocked"):
            _update_task_status(config, task_id, status)
        
        return f"✓ Progress logged: {task_id} - {status}"
        
    except Exception as e:
        return f"⚠️ Failed to log progress: {e}"


def _update_task_status(config: ContextEngineConfig, task_id: str, status: str) -> None:
    """Update task status marker in the work plan file.
    
    Finds the task by ID and updates its status marker.
    """
    tasks_path = config.get_doc_path("tasks")
    if not tasks_path.exists():
        return
    
    # Map status to marker
    marker_map = {
        "started": "[/]",
        "complete": "[x]",
        "blocked": "[B]",
    }
    new_marker = marker_map.get(status)
    if not new_marker:
        return
    
    try:
        content = tasks_path.read_text()
        
        # Pattern: find task ID and update preceding marker
        # Matches: | [x] 1.2.3 | or | [ ] 1.2.3 | or - [ ] 1.2.3
        # We look for the task_id and update the marker before it
        pattern = rf"(\[\s*[xX/B ]?\s*\])\s*{re.escape(task_id)}\b"
        
        updated_content = re.sub(pattern, f"{new_marker} {task_id}", content)
        
        if updated_content != content:
            tasks_path.write_text(updated_content)
            
    except Exception:
        # Silently fail - logging is best effort
        pass


# =============================================================================
# Server entry point
# =============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ContextEngine MCP Server",
        prog="context-engine",
    )
    parser.add_argument(
        "--project",
        type=Path,
        required=True,
        help="Path to the target project directory",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the context-engine CLI."""
    args = parse_args()
    
    # Load and set global config
    project_path = args.project.resolve()
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    config = load_config(project_path)
    set_config(config)
    
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
