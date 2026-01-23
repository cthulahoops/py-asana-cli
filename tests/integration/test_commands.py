"""Integration tests for CLI commands."""

import json

import pytest
import respx
from httpx import Response
from typer.testing import CliRunner

from asana_cli.main import app
from tests.fixtures import responses

runner = CliRunner()


@pytest.fixture
def env_token(monkeypatch):
    """Set API token in environment."""
    # Clear settings cache before and after test
    from asana_cli.config.settings import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("ASANA_TOKEN", "test-token-12345")
    yield
    get_settings.cache_clear()


@pytest.fixture
def env_workspace(monkeypatch):
    """Set default workspace in environment."""
    monkeypatch.setenv("ASANA_WORKSPACE", "workspace1")


class TestConfigCommands:
    """Tests for config commands."""

    def test_config_show_no_token(self, tmp_path, monkeypatch):
        """Test config show with no configuration."""
        monkeypatch.delenv("ASANA_TOKEN", raising=False)
        monkeypatch.setattr("asana_cli.config.storage.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("asana_cli.config.storage.CONFIG_FILE", tmp_path / "config.json")

        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "Not set" in result.output

    def test_config_set_token(self, tmp_path, monkeypatch):
        """Test setting API token."""
        monkeypatch.setattr("asana_cli.config.storage.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("asana_cli.config.storage.CONFIG_FILE", tmp_path / "config.json")

        result = runner.invoke(app, ["config", "set-token", "test-token-abc123"])
        assert result.exit_code == 0
        assert "Token saved" in result.output

        # Verify token was saved
        config_file = tmp_path / "config.json"
        assert config_file.exists()
        config = json.loads(config_file.read_text())
        assert config["token"] == "test-token-abc123"


class TestWorkspaceCommands:
    """Tests for workspace commands."""

    def test_workspaces_list(self, env_token):
        """Test listing workspaces."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/workspaces").mock(
                return_value=Response(200, json=responses.WORKSPACES)
            )

            result = runner.invoke(app, ["workspaces", "list"])
            assert result.exit_code == 0
            assert "Workspace One" in result.output
            assert "Workspace Two" in result.output

    def test_workspaces_list_json(self, env_token):
        """Test listing workspaces with JSON output."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/workspaces").mock(
                return_value=Response(200, json=responses.WORKSPACES)
            )

            result = runner.invoke(app, ["workspaces", "list", "-o", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert len(data) == 2


class TestProjectCommands:
    """Tests for project commands."""

    def test_projects_list(self, env_token, env_workspace):
        """Test listing projects."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects").mock(
                return_value=Response(200, json=responses.PROJECTS)
            )

            result = runner.invoke(app, ["projects", "list"])
            assert result.exit_code == 0
            assert "Project One" in result.output

    def test_projects_get(self, env_token):
        """Test getting project details."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects/project1").mock(
                return_value=Response(200, json=responses.PROJECT_DETAIL)
            )

            result = runner.invoke(app, ["projects", "get", "project1"])
            assert result.exit_code == 0
            assert "Project One" in result.output
            assert "project1" in result.output

    def test_projects_get_not_found(self, env_token):
        """Test getting non-existent project."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects/invalid").mock(
                return_value=Response(404, json=responses.ERROR_NOT_FOUND)
            )

            result = runner.invoke(app, ["projects", "get", "invalid"])
            assert result.exit_code == 1
            assert "not found" in result.output


class TestTaskCommands:
    """Tests for task commands."""

    def test_tasks_list_by_project(self, env_token):
        """Test listing tasks by project."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks").mock(return_value=Response(200, json=responses.TASKS))

            result = runner.invoke(app, ["tasks", "list", "-p", "project1"])
            assert result.exit_code == 0
            assert "Task One" in result.output

    def test_tasks_list_no_filter(self, env_token):
        """Test listing tasks without filter fails."""
        result = runner.invoke(app, ["tasks", "list"])
        assert result.exit_code == 1
        assert "Specify --project or --assignee" in result.output

    def test_tasks_get(self, env_token):
        """Test getting task details."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks/task1").mock(
                return_value=Response(200, json=responses.TASK_DETAIL)
            )

            result = runner.invoke(app, ["tasks", "get", "task1"])
            assert result.exit_code == 0
            assert "Task One" in result.output
            assert "Task description" in result.output

    def test_tasks_create(self, env_token):
        """Test creating a task."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.post("/tasks").mock(
                return_value=Response(201, json=responses.TASK_CREATED)
            )

            result = runner.invoke(app, ["tasks", "create", "New Task", "-p", "project1"])
            assert result.exit_code == 0
            assert "Created task" in result.output
            assert "New Task" in result.output

    def test_tasks_complete(self, env_token):
        """Test completing a task."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.put("/tasks/task1").mock(
                return_value=Response(200, json=responses.TASK_UPDATED)
            )

            result = runner.invoke(app, ["tasks", "complete", "task1"])
            assert result.exit_code == 0
            assert "Completed" in result.output

    def test_tasks_update(self, env_token):
        """Test updating a task."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.put("/tasks/task1").mock(
                return_value=Response(200, json=responses.TASK_UPDATED)
            )

            result = runner.invoke(app, ["tasks", "update", "task1", "--name", "Updated Task"])
            assert result.exit_code == 0
            assert "Updated" in result.output

    def test_tasks_update_no_changes(self, env_token):
        """Test update with no changes fails."""
        result = runner.invoke(app, ["tasks", "update", "task1"])
        assert result.exit_code == 1
        assert "No updates specified" in result.output

    def test_tasks_subtasks(self, env_token):
        """Test listing subtasks."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks/task1/subtasks").mock(
                return_value=Response(200, json=responses.SUBTASKS)
            )

            result = runner.invoke(app, ["tasks", "subtasks", "task1"])
            assert result.exit_code == 0
            assert "Subtask One" in result.output

    def test_tasks_add_subtask(self, env_token):
        """Test creating a subtask."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.post("/tasks/task1/subtasks").mock(
                return_value=Response(201, json=responses.TASK_CREATED)
            )

            result = runner.invoke(app, ["tasks", "add-subtask", "task1", "New Subtask"])
            assert result.exit_code == 0
            assert "Created subtask" in result.output

    def test_tasks_move(self, env_token):
        """Test moving a task to a section."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.post("/sections/section1/addTask").mock(
                return_value=Response(200, json={"data": {}})
            )

            result = runner.invoke(app, ["tasks", "move", "task1", "-s", "section1"])
            assert result.exit_code == 0
            assert "Moved task" in result.output


class TestSectionCommands:
    """Tests for section commands."""

    def test_sections_list(self, env_token):
        """Test listing sections."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects/project1/sections").mock(
                return_value=Response(200, json=responses.SECTIONS)
            )

            result = runner.invoke(app, ["sections", "list", "-p", "project1"])
            assert result.exit_code == 0
            assert "To Do" in result.output
            assert "In Progress" in result.output

    def test_sections_tasks(self, env_token):
        """Test listing tasks in a section."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/sections/section1/tasks").mock(
                return_value=Response(200, json=responses.TASKS)
            )

            result = runner.invoke(app, ["sections", "tasks", "section1"])
            assert result.exit_code == 0
            assert "Task One" in result.output


class TestUserCommands:
    """Tests for user commands."""

    def test_users_me(self, env_token):
        """Test getting current user."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/me").mock(
                return_value=Response(200, json=responses.USER_ME)
            )

            result = runner.invoke(app, ["users", "me"])
            assert result.exit_code == 0
            assert "Test User" in result.output
            assert "test@example.com" in result.output

    def test_users_get(self, env_token):
        """Test getting user by GID."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/67890").mock(
                return_value=Response(200, json=responses.USER_DETAIL)
            )

            result = runner.invoke(app, ["users", "get", "67890"])
            assert result.exit_code == 0
            assert "Other User" in result.output


class TestErrorHandling:
    """Tests for error handling in commands."""

    def test_no_token_error(self, monkeypatch):
        """Test error when no token configured."""
        monkeypatch.delenv("ASANA_TOKEN", raising=False)
        # Clear settings cache
        from asana_cli.config.settings import get_settings
        get_settings.cache_clear()

        result = runner.invoke(app, ["workspaces", "list"])
        assert result.exit_code == 1
        assert "No API token" in result.output

    def test_auth_error(self, env_token):
        """Test authentication error handling."""
        with respx.mock(base_url="https://app.asana.com/api/1.0", assert_all_called=False) as respx_mock:
            respx_mock.get("/workspaces").mock(
                return_value=Response(401, json=responses.ERROR_UNAUTHORIZED)
            )

            result = runner.invoke(app, ["workspaces", "list"])
            assert result.exit_code == 1
