"""Configuration loading for ContextEngine."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ContextEngineConfig:
    """Configuration for a project using ContextEngine.
    
    Loaded from .context-engine.yaml in the target project root.
    """
    
    project_path: Path
    """Path to the target project root."""
    
    commands: dict[str, str] = field(default_factory=lambda: {
        "check": "echo 'No check command configured'",
        "test": "echo 'No test command configured'",
        "build": "echo 'No build command configured'",
        "run": "echo 'No run command configured'",
    })
    """Commands for build, test, etc."""
    
    docs: dict[str, str] = field(default_factory=lambda: {
        "rules": "AGENT.md",
        "tasks": "WORK_PLAN.md",
        "log": "WORK_LOG.md",
        "index": "INDEX.md",
        "readme": "README.md",
    })
    """Paths to documentation files (relative to project root)."""
    
    def get_doc_path(self, doc_name: str) -> Path:
        """Get absolute path to a documentation file."""
        relative_path = self.docs.get(doc_name, f"{doc_name}.md")
        return self.project_path / relative_path
    
    def get_command(self, command_name: str) -> str:
        """Get a configured command by name."""
        return self.commands.get(
            command_name, 
            f"echo 'No {command_name} command configured'"
        )


def load_config(project_path: str | Path) -> ContextEngineConfig:
    """Load configuration from a project directory.
    
    Looks for .context-engine.yaml in the project root.
    Falls back to defaults if not found.
    
    Args:
        project_path: Path to the project root directory.
        
    Returns:
        Loaded configuration with defaults for missing values.
    """
    project_path = Path(project_path).resolve()
    config_file = project_path / ".context-engine.yaml"
    
    config_data: dict[str, Any] = {}
    
    if config_file.exists():
        with open(config_file) as f:
            config_data = yaml.safe_load(f) or {}
    
    # Merge with defaults
    default_config = ContextEngineConfig(project_path=project_path)
    
    commands = {**default_config.commands, **config_data.get("commands", {})}
    docs = {**default_config.docs, **config_data.get("docs", {})}
    
    return ContextEngineConfig(
        project_path=project_path,
        commands=commands,
        docs=docs,
    )


# Global config instance - set by server on startup
_current_config: ContextEngineConfig | None = None


def get_config() -> ContextEngineConfig:
    """Get the current configuration.
    
    Raises:
        RuntimeError: If config has not been initialized.
    """
    if _current_config is None:
        raise RuntimeError(
            "ContextEngine config not initialized. "
            "Server must be started with --project argument."
        )
    return _current_config


def set_config(config: ContextEngineConfig) -> None:
    """Set the global configuration instance."""
    global _current_config
    _current_config = config
