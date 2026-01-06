"""MCP Server for ContextEngine workflows."""

import argparse
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult

from .config import ContextEngineConfig, load_config, set_config, get_config

# Create the FastMCP server instance
mcp = FastMCP(
    "ContextEngine",
    instructions="An MCP server for workflows that promote human-engaged agentic coding",
)

# =============================================================================
# Helper Functions
# =============================================================================

def _run_model(model: str, prompt: str) -> str:
    """Run Gemini model via CLI and return stdout."""
    try:
        # Use a reasonable timeout to prevent hanging forever
        # gemini CLI arguments: gemini -m <model> <prompt>
        cmd = ["gemini", "-m", model, prompt]
        
        # Increase Node.js memory limit to 8GB to prevent OOM on large diffs
        import os
        env = os.environ.copy()
        env["NODE_OPTIONS"] = "--max-old-space-size=8192"
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,
            env=env
        )
        if result.returncode != 0:
            raise RuntimeError(f"Model failed: {result.stderr}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise RuntimeError("Model execution timed out")
    except Exception as e:
        raise RuntimeError(f"Failed to run model: {e}")

def _mark_task_complete(config: ContextEngineConfig, task_id: str) -> None:
    """Update task status marker in the work plan file to [x]."""
    tasks_path = config.get_doc_path("tasks")
    if not tasks_path.exists():
        return
    
    try:
        content = tasks_path.read_text()
        # Pattern: find task ID and update preceding marker to [x]
        pattern = rf"(\[\s*[xX/B ]?\s*\])\s*{re.escape(task_id)}\b"
        updated_content = re.sub(pattern, f"[x] {task_id}", content)
        
        if updated_content != content:
            tasks_path.write_text(updated_content)
    except Exception:
        pass

def _append_log(config: ContextEngineConfig, task_id: str, summary: str) -> None:
    """Append success entry to WORK_LOG.md."""
    log_path = config.get_doc_path("log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n**[{timestamp}]** ✅ `{task_id}` (complete): {summary}\n"
    
    try:
        if log_path.exists():
            with open(log_path, "a") as f:
                f.write(entry)
        else:
            with open(log_path, "w") as f:
                f.write(f"# Work Log\n{entry}")
    except Exception:
        pass

# =============================================================================
# New Tools
# =============================================================================

@mcp.tool()
def fetch_context() -> ToolResult:
    """Rapidly load the project's "Mental Model".
    
    Logic: Read and return the combined content of README.md, WORK_PLAN.md, and AGENT.md.
    Do not return full code files.
    """
    return _fetch_context()

def _fetch_context() -> ToolResult:
    config = get_config()
    files_to_read = [
        ("README", config.get_doc_path("readme")),
        ("WORK PLAN", config.get_doc_path("tasks")),
        ("RULES", config.get_doc_path("rules")),
    ]
    
    content_parts = []
    for label, path in files_to_read:
        if path.exists():
            content_parts.append(f"# {label} ({path.name})\n{path.read_text()}")
        else:
            content_parts.append(f"# {label}\n(File not found at {path})")
            
    # Add Tool Guide
    tool_guide = """# Tool Guide

## workflow management
- **fetch_context**: Call this first. Loads the mental model: README, Work Plan, and Rules.
- **consult_logs(query)**: Check the work log (`WORK_LOG.md`) to see what has been done previously or detailed context.
- **update_docs**: Run this after major changes to keep documentation (README, Rules) in sync with the work log.

## processing
- **draft_implementation_plan(requirement)**: Use this to plan before coding. Returns a template to fill out.
- **delegate_implementation(instructions, context_files)**: Use this for **tightly scoped, well-defined** coding tasks. Decompose changes into smaller stages and call this multiple times rather than trying to do too much in one call.
- **attempt_completion(task_id, summary)**: The specific way to FINISH a task. It verifies your work (runs tests), reviews your changes (Critic), and if successful, commits code and updates the log.
"""
    content_parts.append(tool_guide)
            
    return ToolResult(content="\n\n---\n\n".join(content_parts))



@mcp.tool()
def consult_logs(query: str) -> ToolResult:
    """Filter noise from the work log so the agent doesn't have to read the huge file."""
    return _consult_logs(query)

def _consult_logs(query: str) -> ToolResult:
    config = get_config()
    log_path = config.get_doc_path("log")
    
    if not log_path.exists():
        return ToolResult(content="Work log file not found.")
        
    log_content = log_path.read_text()
    
    system_prompt = "You are a log analyzer. Answer the user's query based only on the provided work log history."
    full_prompt = f"{system_prompt}\n\nWork Log:\n{log_content}\n\nQuery: {query}"
    
    try:
        answer = _run_model("gemini-3-flash-preview", full_prompt)
        return ToolResult(content=answer)
    except Exception as e:
        return ToolResult(content=f"Error consulting logs: {e}")



@mcp.tool()
def draft_implementation_plan(requirement: str) -> ToolResult:
    """Force the agent to "think" before acting.
    
    Returns a structured Markdown template for the agent to fill out.
    """
    return _draft_implementation_plan(requirement)

def _draft_implementation_plan(requirement: str) -> ToolResult:
    template = f"""# Implementation Plan - {requirement}

## User Story
{requirement}

## Proposed Changes (Files)
- [ ] [MODIFY] path/to/file
- [ ] [NEW] path/to/new/file

## Verification Plan
- [ ] Automated tests (command to run)
- [ ] Manual verification steps

## Unknowns
- List any questions or risks
"""
    return ToolResult(content=template)



@mcp.tool()
def delegate_implementation(instructions: str, context_files: list[str]) -> ToolResult:
    """Perform heavy-lifting coding tasks via a sub-agent."""
    return _delegate_implementation(instructions, context_files)

def _delegate_implementation(instructions: str, context_files: list[str]) -> ToolResult:
    config = get_config()
    
    context_content = []
    for file_path in context_files:
        try:
            abs_path = (config.project_path / file_path).resolve()
            # Security check
            if not str(abs_path).startswith(str(config.project_path.resolve())):
                context_content.append(f"⚠️ Context file skipped (outside project): {file_path}")
                continue
                
            if abs_path.exists():
                context_content.append(f"# Context File: {file_path}\n{abs_path.read_text()}\n")
            else:
                context_content.append(f"⚠️ Context file not found: {file_path}")
        except Exception as e:
            context_content.append(f"⚠️ Error reading {file_path}: {e}")

    full_context = "\n".join(context_content)
    
    prompt = f"""You are a senior developer. Implement the requested changes. Output the modified code clearly.

Context:
{full_context}

Instructions:
{instructions}

You only have one turn to complete this task.
If the requirements are not completely clear, you MUST ask for clarification, and NOT MAKE ANY CHANGES.
ONLY if the requirements are clear and you have all the information you need, you must implement the changes in one turn.
"""
    try:
        result = _run_model("gemini-3-pro-preview", prompt)
        return ToolResult(content=result)
    except Exception as e:
        return ToolResult(content=f"Error delegating implementation: {e}")



@mcp.tool()
def attempt_completion(task_id: str, summary: str) -> ToolResult:
    """The "Gatekeeper" tool. Merges review, verification, and finishing."""
    return _attempt_completion(task_id, summary)

def _attempt_completion(task_id: str, summary: str) -> ToolResult:
    config = get_config()
    
    # 1. Verification
    verify_cmd = config.get_command("test")
    print(f"Running verification: {verify_cmd}")
    
    verification = subprocess.run(
        verify_cmd, 
        shell=True,
        cwd=config.project_path, 
        capture_output=True, 
        text=True
    )
    
    if verification.returncode != 0:
        return ToolResult(content=f"❌ Verification Failed:\n{verification.stdout}\n{verification.stderr}")

    # 2. Critic Review
    # Get changes
    # Exclude lockfiles and binary assets to prevent OOM and token waste
    exclusions = [
        ":(exclude)package-lock.json",
        ":(exclude)yarn.lock",
        ":(exclude)pnpm-lock.yaml",
        ":(exclude)Cargo.lock",
        ":(exclude)*.svg",
        ":(exclude)*.png",
        ":(exclude)*.jpg"
    ]
    
    cmd = ["git", "diff", "HEAD"] + exclusions
    
    diff_proc = subprocess.run(
        cmd, 
        cwd=config.project_path, 
        capture_output=True, 
        text=True
    )
    changes = diff_proc.stdout
    if not changes:
         # Maybe staged changes?
        cmd_cached = ["git", "diff", "--cached"] + exclusions
        diff_proc_cached = subprocess.run(
            cmd_cached, 
            cwd=config.project_path, 
            capture_output=True, 
            text=True
        )
        changes = diff_proc_cached.stdout

    if not changes:
        return ToolResult(content="❌ No changes detected to review.")

    critic_prompt = f"""You are a Ruthless Code Reviewer. Review these changes for bugs, security issues, and alignment with the summary. 
Respond with 'APPROVE' or 'REJECT' followed by your reasoning.

Task Summary: {summary}
Changes:
{changes}
"""

    try:
        critic_response = _run_model("gemini-3-pro-preview", critic_prompt)
    except Exception as e:
        return ToolResult(content=f"Error running Critic: {e}")

    if "APPROVE" not in critic_response.upper():
        return ToolResult(content=f"❌ Critic Rejected (or did not approve):\n{critic_response}")

    # 3. Finalize
    try:
        subprocess.run(["git", "add", "."], cwd=config.project_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"feat: {task_id} {summary}"], 
            cwd=config.project_path, 
            check=True
        )
        
        _mark_task_complete(config, task_id)
        _append_log(config, task_id, summary)
        
        return ToolResult(content=f"✅ Task {task_id} Completed, Verified, and Committed.")
        
    except subprocess.CalledProcessError as e:
        return ToolResult(content=f"❌ Failed to commit: {e}")



@mcp.tool()
def update_docs() -> ToolResult:
    """Review work log and update documentation files with relevant information.
    
    Uses a subagent to scan documentation against the work log and apply updates.
    """
    return _update_docs()

def _update_docs() -> ToolResult:
    config = get_config()
    log_path = config.get_doc_path("log")
    
    if not log_path.exists():
        return ToolResult(content="Work log file not found.")
        
    log_content = log_path.read_text()
    updated_files = []
    
    # Iterate over all configured docs, skipping the log itself and tasks
    # We want to update things like README, rules, index, etc.
    skip_keys = {"log", "tasks"}
    
    for doc_key, rel_path in config.docs.items():
        if doc_key in skip_keys:
            continue
            
        doc_path = config.project_path / rel_path
        if not doc_path.exists():
            continue
            
        current_content = doc_path.read_text()
        
        prompt = f"""You are a Documentation Maintainer. Your goal is to keep the documentation up-to-date with the work log.
        
Think very carefully about whether the information in the work log is relevant to this specific documentation file.
If the information is just implementation details that don't belong in high-level docs, ignore it.
If the information contradicts current docs or adds new features that should be documented, update it.

Work Log:
{log_content}

Current File ({doc_key} - {rel_path}):
{current_content}

Instructions:
1. Analyze if changes are needed.
2. If NO changes are needed, output exactly: NO_CHANGES
3. If changes ARE needed, output the FULL new content of the file. Do not use diffs. Output only the content.
"""
        try:
            # We use flash for speed/cost, or pro for quality? Plan said pro.
            # "Uses a subagent (gemini-3-pro-preview)..."
            new_content = _run_model("gemini-3-pro-preview", prompt)
            
            if "NO_CHANGES" in new_content:
                continue
                
            # Sanity check: if it returned empty string or something weird
            if not new_content.strip():
                continue
                
            if new_content != current_content:
                doc_path.write_text(new_content)
                updated_files.append(f"{rel_path}")
                
        except Exception as e:
            print(f"Failed to update {rel_path}: {e}")
            
    if not updated_files:
        return ToolResult(content="Documentation review complete. No updates needed.")
        
    return ToolResult(content=f"✅ Updated documentation files: {', '.join(updated_files)}")


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
