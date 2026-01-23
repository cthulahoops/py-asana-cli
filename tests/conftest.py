"""Pytest configuration and fixtures."""

import pytest
import respx
from httpx import Response

from tests.fixtures import responses


@pytest.fixture
def mock_api():
    """Create a respx mock for Asana API."""
    with respx.mock(base_url="https://app.asana.com/api/1.0", assert_all_called=False) as mock:
        yield mock


@pytest.fixture
def mock_api_with_auth(mock_api):
    """Mock API with standard auth-required endpoints configured."""
    # Users
    mock_api.get("/users/me").mock(return_value=Response(200, json=responses.USER_ME))
    mock_api.get("/users/67890").mock(return_value=Response(200, json=responses.USER_DETAIL))

    # Workspaces
    mock_api.get("/workspaces").mock(return_value=Response(200, json=responses.WORKSPACES))

    # Projects
    mock_api.get("/projects", params__contains={"workspace": "workspace1"}).mock(
        return_value=Response(200, json=responses.PROJECTS)
    )
    mock_api.get("/projects/project1").mock(
        return_value=Response(200, json=responses.PROJECT_DETAIL)
    )

    # Sections
    mock_api.get("/projects/project1/sections").mock(
        return_value=Response(200, json=responses.SECTIONS)
    )
    mock_api.get("/sections/section1/tasks").mock(
        return_value=Response(200, json=responses.TASKS)
    )

    # Tasks
    mock_api.get("/tasks", params__contains={"project": "project1"}).mock(
        return_value=Response(200, json=responses.TASKS)
    )
    mock_api.get("/tasks/task1").mock(return_value=Response(200, json=responses.TASK_DETAIL))
    mock_api.get("/tasks/task1/subtasks").mock(
        return_value=Response(200, json=responses.SUBTASKS)
    )
    mock_api.post("/tasks").mock(return_value=Response(201, json=responses.TASK_CREATED))
    mock_api.put("/tasks/task1").mock(return_value=Response(200, json=responses.TASK_UPDATED))
    mock_api.post("/tasks/task1/subtasks").mock(
        return_value=Response(201, json=responses.TASK_CREATED)
    )
    mock_api.post("/sections/section1/addTask").mock(return_value=Response(200, json={"data": {}}))

    return mock_api


@pytest.fixture
def mock_token(monkeypatch):
    """Mock the API token."""
    monkeypatch.setenv("ASANA_TOKEN", "test-token-12345")


@pytest.fixture
def mock_workspace(monkeypatch):
    """Mock the default workspace."""
    monkeypatch.setenv("ASANA_WORKSPACE", "workspace1")
