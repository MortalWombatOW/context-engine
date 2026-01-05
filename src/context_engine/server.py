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
def start() -> ToolResult:
    """Load the complete mental model of the project.
    
    Run at the start of a session before beginning work.
    Reads project rules, index, readme, and task list.
    """
    content = render_workflow("start")
    return ToolResult(content=content)


@mcp.tool()
def plan(
    requirement: str | None = None,
    delegate: bool = False
) -> ToolResult:
    """Research context and convert requirements into atomic tasks.
    
    Run when planning new work. Analyzes the request against project rules
    and creates a micro-plan of tasks.
    
    Args:
        requirement: Optional description of the feature/change to plan.
        delegate: If True, execute the prompt with a subagent.
    """
    content = render_workflow("plan")
    if requirement:
        content = f"# Requirement\n\n{requirement}\n\n---\n\n{content}"
    
    if delegate:
        return _delegate_impl(content, high_complexity=True)
    return ToolResult(content=content)


@mcp.tool()
def execute_task(
    task_id: str | None = None,
    delegate: bool = False,
    high_complexity: bool = False
) -> ToolResult:
    """Select the next task and implement it with high quality.
    
    Run after start or finish to find what to work on next.
    Selects the next available task, marks it in-progress, and implements it.
    Includes checkpoints for documentation via log_progress.
    
    Args:
        task_id: Optional specific task ID to implement (skips selection).
        delegate: If True, execute the prompt with a subagent.
        high_complexity: If True, use reasoning-capable model (gemini-3-pro-preview).
    """
    content = render_workflow("execute-task")
    if task_id:
        content = f"# Active Task: {task_id}\n\n---\n\n{content}"
    
    if delegate:
        return _delegate_impl(content, high_complexity=high_complexity)
    return ToolResult(content=content)


@mcp.tool()
def review() -> ToolResult:
    """Comprehensive code review to ensure quality.
    
    Run after execute_task to review implemented changes.
    Checks code quality, architectural alignment, and documentation.
    """
    return _delegate_impl(render_workflow("review"), high_complexity=False)



@mcp.tool()
def finish() -> ToolResult:
    """Mark work complete and persist changes.
    
    Run after review passes to finalize the task.
    Updates task status, logs completion, and commits changes.
    """
    return ToolResult(content=render_workflow("finish"))


@mcp.tool()
def summarize() -> ToolResult:
    """Prepare handoff for next agent session.
    
    Run when ending a session or hitting a complex blocker.
    Creates a handoff note with current state and next steps.
    """
    return ToolResult(content=render_workflow("summarize"))


@mcp.tool()
def refine() -> ToolResult:
    """Maintain documentation and improve process.
    
    Run periodically to sync documentation with code changes
    and identify process improvements.
    """
    return ToolResult(content=render_workflow("refine"))

@mcp.tool()
def delegate(
    prompt: str,
    context_files: list[str] | None = None,
    high_complexity: bool = False,
    timeout: int | None = None,
) -> ToolResult:
    """Delegate a task to a Gemini subagent.
    
    Spawns a new Gemini CLI instance to handle a specific task,
    reducing token usage by the main agent.
    
    Args:
        prompt: The task description for the subagent.
        context_files: List of file paths (relative to project root) to read and pass to the subagent.
        high_complexity: If True, use reasoning-capable model (gemini-3-pro-preview).
                         Otherwise, use fast model (gemini-3-flash-preview).
        timeout: Maximum seconds to wait (default: configured timeout).
    
    Returns:
        The subagent's response.
    """
    return _delegate_impl(prompt, context_files, high_complexity, timeout)


def _delegate_impl(
    prompt: str,
    context_files: list[str] | None = None,
    high_complexity: bool = False,
    timeout: int | None = None
) -> ToolResult:
    """Implementation of delegate tool."""
    import subprocess
    
    config = get_config()
    
    # Select model based on complexity flag
    target_model = "gemini-3-pro-preview" if high_complexity else "gemini-3-flash-preview"
    # Cast safely - config values might be parsed as strings from YAML
    timeout_val = int(timeout or config.delegation["timeout"])
    
    # Construct the full prompt with context files
    preamble = (
        "SYSTEM NOTE: You are a subagent working on a specific task. "
        "You have only ONE turn to complete this task. "
        "You are stateless; no memory is retained after this turn. "
        "You must tie up all loose ends within this single response. "
        "If the task is too large to complete in a single turn, you must explicitly state this."
    )
    
    full_prompt = f"{preamble}\n\n{prompt}"
    if context_files:
        context_content = []
        for file_path in context_files:
            try:
                # Resolve path relative to project root
                abs_path = (config.project_path / file_path).resolve()
                
                # Security check: ensure path is within project
                if not str(abs_path).startswith(str(config.project_path.resolve())):
                    context_content.append(f"⚠️ Context file skipped (outside project): {file_path}")
                    continue
                    
                if abs_path.exists():
                    file_text = abs_path.read_text()
                    context_content.append(f"# Context File: {file_path}\n{file_text}\n")
                else:
                    context_content.append(f"⚠️ Context file not found: {file_path}")
            except Exception as e:
                context_content.append(f"⚠️ Error reading {file_path}: {e}")
        
        if context_content:
            full_prompt = f"{preamble}\n\n" + "\n".join(context_content) + "\n\n---\n\n" + prompt

    try:
        # Construct the command
        # gemini -m "model" "prompt"
        # We use the positional prompt argument which is the preferred way
        cmd = ["gemini", "-m", str(target_model), full_prompt]
        
        # Run execution in the project directory
        result = subprocess.run(
            cmd,
            cwd=config.project_path,
            capture_output=True,
            text=True,
            timeout=timeout_val,
        )
        
        if result.returncode != 0:
            return ToolResult(content=f"⚠️ Subagent failed (exit code {result.returncode}):\n{result.stderr}")
            
        return ToolResult(content=result.stdout.strip())
        
    except subprocess.TimeoutExpired:
        return ToolResult(content=f"⚠️ Subagent timed out after {timeout_val} seconds")
    except Exception as e:
        return ToolResult(content=f"⚠️ Failed to delegate task: {str(e)}")


# =============================================================================
# Documentation Tool - Progress logging
# =============================================================================

@mcp.tool()
def log_progress(
    task_id: str,
    status: Literal["started", "implementing", "verified", "blocked", "complete"],
    summary: str,
) -> ToolResult:
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
        
        return ToolResult(content=f"✓ Progress logged: {task_id} - {status}")
        
    except Exception as e:
        return ToolResult(content=f"⚠️ Failed to log progress: {e}")


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
