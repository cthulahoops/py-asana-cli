"""Unit tests for Asana API client."""

import pytest
import respx
from httpx import Response

from asana_cli.client import (
    AsanaAPIError,
    AsanaClient,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    RateLimitError,
)
from tests.fixtures import responses


@pytest.fixture
def env_token(monkeypatch):
    """Set API token in environment."""
    # Clear settings cache before and after test
    from asana_cli.config.settings import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("ASANA_TOKEN", "test-token-12345")
    yield
    get_settings.cache_clear()


class TestClientInit:
    """Tests for client initialization."""

    def test_init_with_token(self):
        """Test client initialization with provided token."""
        with respx.mock:
            client = AsanaClient(token="test-token")
            assert client._token == "test-token"
            client.close()

    def test_init_from_env(self, env_token):
        """Test client initialization from environment variable."""
        with respx.mock:
            client = AsanaClient()
            assert client._token == "test-token-12345"
            client.close()

    def test_init_no_token_raises(self, monkeypatch):
        """Test that missing token raises ConfigurationError."""
        monkeypatch.delenv("ASANA_TOKEN", raising=False)
        from asana_cli.config.settings import get_settings
        get_settings.cache_clear()

        with pytest.raises(ConfigurationError, match="No API token configured"):
            AsanaClient()

    def test_context_manager(self, env_token):
        """Test client as context manager."""
        with respx.mock, AsanaClient() as client:
            assert client._token == "test-token-12345"


class TestClientErrorHandling:
    """Tests for client error handling."""

    def test_401_raises_authentication_error(self, env_token):
        """Test 401 response raises AuthenticationError."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/me").mock(
                return_value=Response(401, json=responses.ERROR_UNAUTHORIZED)
            )

            with pytest.raises(AuthenticationError, match="Not authorized"):
                with AsanaClient() as client:
                    client.get_me()

    def test_404_raises_not_found_error(self, env_token):
        """Test 404 response raises NotFoundError."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks/invalid").mock(
                return_value=Response(404, json=responses.ERROR_NOT_FOUND)
            )

            with pytest.raises(NotFoundError, match="Resource not found"):
                with AsanaClient() as client:
                    client.get_task("invalid")

    def test_429_raises_rate_limit_error(self, env_token):
        """Test 429 response raises RateLimitError."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/me").mock(
                return_value=Response(429, json={"errors": [{"message": "Rate limit exceeded"}]})
            )

            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                with AsanaClient() as client:
                    client.get_me()

    def test_500_raises_api_error(self, env_token):
        """Test 500 response raises AsanaAPIError."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/me").mock(
                return_value=Response(500, json={"errors": [{"message": "Internal error"}]})
            )

            with pytest.raises(AsanaAPIError, match="Internal error"):
                with AsanaClient() as client:
                    client.get_me()


class TestUserEndpoints:
    """Tests for user-related endpoints."""

    def test_get_me(self, env_token):
        """Test getting current user."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/me").mock(
                return_value=Response(200, json=responses.USER_ME)
            )

            with AsanaClient() as client:
                user = client.get_me()

            assert user["gid"] == "12345"
            assert user["name"] == "Test User"
            assert user["email"] == "test@example.com"

    def test_get_user(self, env_token):
        """Test getting user by GID."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/users/67890").mock(
                return_value=Response(200, json=responses.USER_DETAIL)
            )

            with AsanaClient() as client:
                user = client.get_user("67890")

            assert user["gid"] == "67890"
            assert user["name"] == "Other User"


class TestWorkspaceEndpoints:
    """Tests for workspace-related endpoints."""

    def test_get_workspaces(self, env_token):
        """Test getting workspaces."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/workspaces").mock(
                return_value=Response(200, json=responses.WORKSPACES)
            )

            with AsanaClient() as client:
                workspaces = client.get_workspaces()

            assert len(workspaces) == 2
            assert workspaces[0]["name"] == "Workspace One"


class TestProjectEndpoints:
    """Tests for project-related endpoints."""

    def test_get_projects(self, env_token):
        """Test getting projects."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects").mock(
                return_value=Response(200, json=responses.PROJECTS)
            )

            with AsanaClient() as client:
                projects = client.get_projects("workspace1")

            assert len(projects) == 2
            assert projects[0]["name"] == "Project One"

    def test_get_project(self, env_token):
        """Test getting project details."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects/project1").mock(
                return_value=Response(200, json=responses.PROJECT_DETAIL)
            )

            with AsanaClient() as client:
                project = client.get_project("project1")

            assert project["gid"] == "project1"
            assert project["name"] == "Project One"


class TestSectionEndpoints:
    """Tests for section-related endpoints."""

    def test_get_sections(self, env_token):
        """Test getting sections."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/projects/project1/sections").mock(
                return_value=Response(200, json=responses.SECTIONS)
            )

            with AsanaClient() as client:
                sections = client.get_sections("project1")

            assert len(sections) == 3
            assert sections[0]["name"] == "To Do"

    def test_get_section_tasks(self, env_token):
        """Test getting tasks in a section."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/sections/section1/tasks").mock(
                return_value=Response(200, json=responses.TASKS)
            )

            with AsanaClient() as client:
                tasks = client.get_section_tasks("section1")

            assert len(tasks) == 2


class TestTaskEndpoints:
    """Tests for task-related endpoints."""

    def test_get_tasks_by_project(self, env_token):
        """Test getting tasks by project."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks").mock(
                return_value=Response(200, json=responses.TASKS)
            )

            with AsanaClient() as client:
                tasks = client.get_tasks(project="project1")

            assert len(tasks) == 2
            assert tasks[0]["name"] == "Task One"

    def test_get_task(self, env_token):
        """Test getting task details."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks/task1").mock(
                return_value=Response(200, json=responses.TASK_DETAIL)
            )

            with AsanaClient() as client:
                task = client.get_task("task1")

            assert task["gid"] == "task1"
            assert task["name"] == "Task One"

    def test_create_task(self, env_token):
        """Test creating a task."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.post("/tasks").mock(
                return_value=Response(201, json=responses.TASK_CREATED)
            )

            with AsanaClient() as client:
                task = client.create_task({"name": "New Task", "projects": ["project1"]})

            assert task["gid"] == "newtask"
            assert task["name"] == "New Task"

    def test_update_task(self, env_token):
        """Test updating a task."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.put("/tasks/task1").mock(
                return_value=Response(200, json=responses.TASK_UPDATED)
            )

            with AsanaClient() as client:
                task = client.update_task("task1", {"completed": True})

            assert task["completed"] is True

    def test_get_subtasks(self, env_token):
        """Test getting subtasks."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/tasks/task1/subtasks").mock(
                return_value=Response(200, json=responses.SUBTASKS)
            )

            with AsanaClient() as client:
                subtasks = client.get_subtasks("task1")

            assert len(subtasks) == 2
            assert subtasks[0]["name"] == "Subtask One"

    def test_create_subtask(self, env_token):
        """Test creating a subtask."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.post("/tasks/task1/subtasks").mock(
                return_value=Response(201, json=responses.TASK_CREATED)
            )

            with AsanaClient() as client:
                subtask = client.create_subtask("task1", {"name": "New Subtask"})

            assert subtask["name"] == "New Task"

    def test_add_task_to_section(self, env_token):
        """Test moving task to section."""
        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.post("/sections/section1/addTask").mock(
                return_value=Response(200, json={"data": {}})
            )

            with AsanaClient() as client:
                # Should not raise
                client.add_task_to_section("section1", "task1")


class TestPagination:
    """Tests for pagination handling."""

    def test_pagination_follows_next_page(self, env_token):
        """Test that pagination follows next_page links."""
        page1 = {
            "data": [{"gid": "1", "name": "Item 1"}],
            "next_page": {"offset": "abc123", "path": "/workspaces", "uri": "..."},
        }
        page2 = {
            "data": [{"gid": "2", "name": "Item 2"}],
            "next_page": None,
        }

        with respx.mock(base_url="https://app.asana.com/api/1.0") as respx_mock:
            respx_mock.get("/workspaces").mock(
                side_effect=[Response(200, json=page1), Response(200, json=page2)]
            )

            with AsanaClient() as client:
                workspaces = client.get_workspaces()

            assert len(workspaces) == 2
            assert workspaces[0]["gid"] == "1"
            assert workspaces[1]["gid"] == "2"
