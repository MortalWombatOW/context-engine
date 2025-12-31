"""Tests for ContextEngine."""

import tempfile
from pathlib import Path

import pytest

from context_engine.config import ContextEngineConfig, load_config, set_config, get_config
from context_engine.templates import render_workflow, list_workflows


# =============================================================================
# Config Tests
# =============================================================================

class TestConfig:
    """Tests for configuration loading."""
    
    def test_load_config_defaults(self, tmp_path: Path):
        """Test loading config from directory without config file."""
        config = load_config(tmp_path)
        
        assert config.project_path == tmp_path
        assert "check" in config.commands
        assert config.docs["rules"] == "AGENT.md"
        assert config.docs["tasks"] == "WORK_PLAN.md"
    
    def test_load_config_with_file(self, tmp_path: Path):
        """Test loading config from .context-engine.yaml."""
        config_content = """
commands:
  check: "pytest"
  test: "pytest -v"

docs:
  rules: "CONTRIBUTING.md"
  tasks: "TODO.md"
"""
        config_file = tmp_path / ".context-engine.yaml"
        config_file.write_text(config_content)
        
        config = load_config(tmp_path)
        
        assert config.commands["check"] == "pytest"
        assert config.commands["test"] == "pytest -v"
        assert config.docs["rules"] == "CONTRIBUTING.md"
        assert config.docs["tasks"] == "TODO.md"
        # Defaults should still be present for unspecified keys
        assert config.docs["log"] == "WORK_LOG.md"
    
    def test_get_doc_path(self, tmp_path: Path):
        """Test getting absolute path to documentation files."""
        config = load_config(tmp_path)
        
        rules_path = config.get_doc_path("rules")
        assert rules_path == tmp_path / "AGENT.md"
    
    def test_global_config(self, tmp_path: Path):
        """Test global config set/get."""
        config = load_config(tmp_path)
        set_config(config)
        
        retrieved = get_config()
        assert retrieved.project_path == tmp_path


# =============================================================================
# Template Tests
# =============================================================================

class TestTemplates:
    """Tests for template rendering."""
    
    @pytest.fixture(autouse=True)
    def setup_config(self, tmp_path: Path):
        """Set up a test config before each test."""
        config = ContextEngineConfig(
            project_path=tmp_path,
            commands={
                "check": "make check",
                "test": "make test",
                "build": "make build",
                "run": "make run",
            },
            docs={
                "rules": "RULES.md",
                "tasks": "TASKS.md",
                "log": "LOG.md",
                "index": "INDEX.md",
                "readme": "README.md",
            },
        )
        set_config(config)
    
    def test_list_workflows(self):
        """Test listing available workflows."""
        workflows = list_workflows()
        
        assert "init" in workflows
        assert "forge" in workflows
        assert "audit" in workflows
        assert "accept" in workflows
        assert len(workflows) == 8
    
    def test_render_init(self):
        """Test rendering the init workflow."""
        content = render_workflow("init")
        
        assert "RULES.md" in content  # Template variable substituted
        assert "INDEX.md" in content
        assert "TASKS.md" in content

    def test_render_init_with_content(self, tmp_path: Path):
        """Test that init workflow inlines file content."""
        # Create dummy doc files
        (tmp_path / "RULES.md").write_text("Rule: Be nice")
        (tmp_path / "INDEX.md").write_text("Map: You are here")
        (tmp_path / "README.md").write_text("Intro: Hello")
        (tmp_path / "TASKS.md").write_text("- [ ] Task 1")
        
        # We need to reload the config to point to these new files?
        # The fixture sets config pointing to these filenames in tmp_path.
        # So we just need to ensure the files exist there.
        
        content = render_workflow("init")
        
        assert "Rule: Be nice" in content
        assert "Map: You are here" in content
        assert "Intro: Hello" in content
        assert "- [ ] Task 1" in content
    
    def test_render_forge(self):
        """Test rendering the forge workflow."""
        content = render_workflow("forge")
        
        assert "make check" in content  # Command substituted
        assert "make test" in content
        assert "TASKS.md" in content
        assert "log_progress" in content  # Checkpoint instruction
    
    def test_render_accept(self):
        """Test rendering the accept workflow."""
        content = render_workflow("accept")
        
        assert "make check" in content
        assert "log_progress" in content
        assert "complete" in content


# =============================================================================
# Server Tests
# =============================================================================

class TestServer:
    """Tests for MCP server components."""
    
    def test_server_exists(self):
        """Test that the MCP server is configured."""
        from context_engine.server import mcp
        assert mcp.name == "ContextEngine"
