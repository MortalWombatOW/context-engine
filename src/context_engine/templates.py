"""Jinja2 template rendering for workflow prompts."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from .config import ContextEngineConfig, get_config


def get_workflows_dir() -> Path:
    """Get the path to the workflows directory."""
    # workflows/ is at the package root, sibling to src/
    package_dir = Path(__file__).parent
    src_dir = package_dir.parent
    repo_root = src_dir.parent
    return repo_root / "workflows"


def create_template_env() -> Environment:
    """Create a Jinja2 environment for workflow templates."""
    workflows_dir = get_workflows_dir()
    return Environment(
        loader=FileSystemLoader(workflows_dir),
        autoescape=False,  # Markdown, not HTML
        trim_blocks=True,
        lstrip_blocks=True,
    )


def load_template(workflow_name: str) -> Template:
    """Load a workflow template by name.
    
    Args:
        workflow_name: Name of the workflow (e.g., 'forge', 'audit').
                      Will load from workflows/{name}.md
    
    Returns:
        Jinja2 Template object.
    """
    env = create_template_env()
    # Handle both 'forge' and 'forge.md' inputs
    if not workflow_name.endswith(".md"):
        workflow_name = f"{workflow_name}.md"
    return env.get_template(workflow_name)


def render_workflow(workflow_name: str, config: ContextEngineConfig | None = None) -> str:
    """Render a workflow template with configuration values.
    
    Args:
        workflow_name: Name of the workflow to render.
        config: Configuration to use. If None, uses global config.
        
    Returns:
        Rendered workflow content as string.
    """
    if config is None:
        config = get_config()
    
    template = load_template(workflow_name)
    
    def read_to_text(filename: str) -> str:
        """Read a file to text, relative to project root."""
        try:
            file_path = config.project_path / filename
            if not file_path.exists():
                return f"Error: File not found: {filename}"
            return file_path.read_text()
        except Exception as e:
            return f"Error reading {filename}: {e}"

    # Build template context from config
    context = {
        "commands": config.commands,
        "docs": config.docs,
        "project_path": str(config.project_path),
        "read_to_text": read_to_text,
    }
    
    return template.render(**context)


def list_workflows() -> list[str]:
    """List all available workflow templates.
    
    Returns:
        List of workflow names (without .md extension).
    """
    workflows_dir = get_workflows_dir()
    return [
        f.stem for f in workflows_dir.glob("*.md")
        if f.is_file()
    ]
