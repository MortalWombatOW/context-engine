"""Tests for ContextEngine."""

import tempfile
from pathlib import Path
import re

import pytest
from fastmcp.tools.tool import ToolResult

from context_engine.config import ContextEngineConfig, load_config, set_config, get_config

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
# Server Tests
# =============================================================================

class TestServer:
    """Tests for MCP server components."""
    
    @pytest.fixture(autouse=True)
    def setup_config(self, tmp_path: Path):
        """Set up a test config before each test."""
        config = ContextEngineConfig(
            project_path=tmp_path,
            commands={
                "check": "echo check",
                "test": "echo verify",
            },
            docs={
                "rules": "RULES.md",
                "tasks": "TASKS.md",
                "log": "LOG.md",
                "readme": "README.md",
            },
        )
        set_config(config)
        # Create dummy files
        (tmp_path / "RULES.md").write_text("Rule: Be nice")
        (tmp_path / "TASKS.md").write_text("- [ ] Task 1")
        (tmp_path / "README.md").write_text("# Readme")
        (tmp_path / "LOG.md").write_text("# Log")

    def test_server_exists(self):
        """Test that the MCP server is configured."""
        from context_engine.server import mcp
        assert mcp.name == "ContextEngine"
    
    def test_fetch_context(self):
        """Test fetch_context tool."""
        from context_engine.server import _fetch_context
        
        result = _fetch_context()
        content = str(result.content) if not hasattr(result, 'content') else str(result.content)
        
        assert "Rule: Be nice" in content
        assert "Task 1" in content
        assert "# Readme" in content
        assert "# Tool Guide" in content
        assert "attempt_completion" in content
        
    def test_draft_implementation_plan(self):
        """Test draft_implementation_plan tool."""
        from context_engine.server import _draft_implementation_plan
        
        result = _draft_implementation_plan(requirement="Fix bug")
        content = str(result.content)
        
        assert "# Implementation Plan - Fix bug" in content
        assert "## User Story" in content
        assert "Fix bug" in content

    def test_consult_logs_mock(self, monkeypatch):
        """Test consult_logs tool with mocked subprocess."""
        import subprocess
        from context_engine.server import _consult_logs
        
        class MockResult:
            returncode = 0
            stdout = "Log analysis result"
            stderr = ""
            
        def mock_run(cmd, **kwargs):
            # Check command structure
            assert cmd[0] == "gemini"
            assert cmd[2] == "gemini-3-flash-preview"
            return MockResult()
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        result = _consult_logs(query="what happened?")
        assert result.content[0].text == "Log analysis result"

    def test_delegate_implementation_mock(self, monkeypatch, tmp_path):
        """Test delegate_implementation tool with mocked subprocess."""
        import subprocess
        from context_engine.server import _delegate_implementation
        
        # Create a context file
        ctx_file = tmp_path / "ctx.py"
        ctx_file.write_text("print('hello')")
        
        class MockResult:
            returncode = 0
            stdout = "Modified code"
            stderr = ""
            
        def mock_run(cmd, **kwargs):
            assert cmd[0] == "gemini"
            assert cmd[2] == "gemini-3-pro-preview"
            # Check that context file content is in the prompt
            assert "print('hello')" in cmd[3]
            return MockResult()
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        result = _delegate_implementation(instructions="improve it", context_files=["ctx.py"])
        assert result.content[0].text == "Modified code"

    def test_update_docs_mock(self, monkeypatch, tmp_path):
        """Test update_docs tool."""
        import subprocess
        from context_engine.server import _update_docs
        
        # Setup doc file
        readme = tmp_path / "README.md"
        # Initial content
        readme.write_text("# Old Readme")
        
        # Mock subprocess
        class MockResult:
            returncode = 0
            stdout = "# New Readme"
            stderr = ""
            
        def mock_run(cmd, **kwargs):
            return MockResult()
            
        monkeypatch.setattr(subprocess, "run", mock_run)
        
        result = _update_docs()
        
        assert "README.md" in result.content[0].text
        assert readme.read_text() == "# New Readme"

