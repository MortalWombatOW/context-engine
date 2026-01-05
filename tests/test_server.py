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
        
        assert "start" in workflows
        assert "execute-task" in workflows
        assert "review" in workflows
        assert "finish" in workflows
        assert len(workflows) == 7
    
    def test_render_start(self):
        """Test rendering the start workflow."""
        content = render_workflow("start")
        
        assert "RULES.md" in content  # Template variable substituted
        assert "INDEX.md" in content
        assert "TASKS.md" in content

    def test_render_start_with_content(self, tmp_path: Path):
        """Test that start workflow inlines file content."""
        # Create dummy doc files
        (tmp_path / "RULES.md").write_text("Rule: Be nice")
        (tmp_path / "INDEX.md").write_text("Map: You are here")
        (tmp_path / "README.md").write_text("Intro: Hello")
        (tmp_path / "TASKS.md").write_text("- [ ] Task 1")
        
        # We need to reload the config to point to these new files?
        # The fixture sets config pointing to these filenames in tmp_path.
        # So we just need to ensure the files exist there.
        
        content = render_workflow("start")
        
        assert "Rule: Be nice" in content
        assert "Map: You are here" in content
        assert "Intro: Hello" in content
        assert "- [ ] Task 1" in content
    
    def test_render_execute_task(self):
        """Test rendering the execute-task workflow."""
        content = render_workflow("execute-task")
        
        assert "make check" in content  # Command substituted
        assert "make test" in content
        assert "TASKS.md" in content
        assert "log_progress" in content  # Checkpoint instruction
    
    def test_render_finish(self):
        """Test rendering the finish workflow."""
        content = render_workflow("finish")
        
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
    
    def test_delegate_tool(self, monkeypatch):
        """Test the delegate tool."""
        import subprocess
        from context_engine.server import _delegate_impl
        
        # Mock subprocess.run
        class MockResult:
            returncode = 0
            stdout = "I am a subagent"
            stderr = ""
            
        params = {}
        
        def mock_run(cmd, **kwargs):
            params["cmd"] = cmd
            params["timeout"] = kwargs.get("timeout")
            return MockResult()
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        # Test with defaults
        result = _delegate_impl(prompt="hello")
        assert result == "I am a subagent"
        assert params["cmd"] == ["gemini", "-m", "gemini-2.0-flash", "hello"]
        assert params["timeout"] == 300
        
        # Test overrides
        result = _delegate_impl(prompt="hi", model="foo", timeout=10)
        assert params["cmd"] == ["gemini", "-m", "foo", "hi"]
        assert params["timeout"] == 10

    def test_delegate_tool_failure(self, monkeypatch):
        """Test delegate tool error handling."""
        import subprocess
        from context_engine.server import _delegate_impl
        
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = "Error message"
            
        def mock_run(*args, **kwargs):
            return MockResult()
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        result = _delegate_impl(prompt="fail")
        assert "Error message" in result
        assert "exit code 1" in result
