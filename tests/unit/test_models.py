"""Unit tests for Pydantic models."""

from datetime import date

from asana_cli.models import (
    Project,
    Section,
    Task,
    TaskCreateRequest,
    TaskUpdateRequest,
    User,
    Workspace,
)


class TestUserModels:
    """Tests for user-related models."""

    def test_user_from_dict(self):
        """Test creating User from dictionary."""
        data = {
            "gid": "12345",
            "name": "Test User",
            "email": "test@example.com",
            "resource_type": "user",
            "workspaces": [
                {"gid": "ws1", "name": "Workspace 1"},
                {"gid": "ws2", "name": "Workspace 2"},
            ],
        }
        user = User.model_validate(data)

        assert user.gid == "12345"
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert len(user.workspaces) == 2
        assert user.workspaces[0].gid == "ws1"

    def test_user_optional_fields(self):
        """Test User with minimal fields."""
        data = {"gid": "12345", "name": "Test User"}
        user = User.model_validate(data)

        assert user.gid == "12345"
        assert user.name == "Test User"
        assert user.email is None
        assert user.workspaces == []

    def test_workspace_model(self):
        """Test Workspace model."""
        ws = Workspace(gid="ws1", name="My Workspace")
        assert ws.gid == "ws1"
        assert ws.name == "My Workspace"


class TestProjectModels:
    """Tests for project-related models."""

    def test_project_from_dict(self):
        """Test creating Project from dictionary."""
        data = {
            "gid": "proj1",
            "name": "Test Project",
            "archived": False,
            "notes": "Project notes",
            "owner": {"gid": "user1", "name": "Owner"},
            "workspace": {"gid": "ws1", "name": "Workspace"},
            "due_on": "2024-12-31",
        }
        project = Project.model_validate(data)

        assert project.gid == "proj1"
        assert project.name == "Test Project"
        assert project.archived is False
        assert project.notes == "Project notes"
        assert project.owner.name == "Owner"
        assert project.due_on == date(2024, 12, 31)

    def test_project_extra_fields_ignored(self):
        """Test that extra fields are ignored."""
        data = {
            "gid": "proj1",
            "name": "Test",
            "unknown_field": "should be ignored",
        }
        project = Project.model_validate(data)
        assert project.gid == "proj1"
        assert not hasattr(project, "unknown_field")


class TestSectionModels:
    """Tests for section-related models."""

    def test_section_from_dict(self):
        """Test creating Section from dictionary."""
        data = {
            "gid": "sec1",
            "name": "To Do",
            "created_at": "2024-01-01T00:00:00.000Z",
            "project": {"gid": "proj1", "name": "Project"},
        }
        section = Section.model_validate(data)

        assert section.gid == "sec1"
        assert section.name == "To Do"
        assert section.project.name == "Project"


class TestTaskModels:
    """Tests for task-related models."""

    def test_task_from_dict(self):
        """Test creating Task from dictionary."""
        data = {
            "gid": "task1",
            "name": "Test Task",
            "completed": False,
            "due_on": "2024-06-15",
            "notes": "Task notes",
            "assignee": {"gid": "user1", "name": "Assignee"},
            "projects": [{"gid": "proj1", "name": "Project"}],
            "num_subtasks": 3,
        }
        task = Task.model_validate(data)

        assert task.gid == "task1"
        assert task.name == "Test Task"
        assert task.completed is False
        assert task.due_on == date(2024, 6, 15)
        assert task.assignee.name == "Assignee"
        assert len(task.projects) == 1

    def test_task_completed(self):
        """Test completed task with completed_at."""
        data = {
            "gid": "task1",
            "name": "Done Task",
            "completed": True,
            "completed_at": "2024-05-01T15:30:00.000Z",
        }
        task = Task.model_validate(data)

        assert task.completed is True
        assert task.completed_at is not None

    def test_task_with_parent(self):
        """Test subtask with parent reference."""
        data = {
            "gid": "subtask1",
            "name": "Subtask",
            "completed": False,
            "parent": {"gid": "task1", "name": "Parent Task", "completed": False},
        }
        task = Task.model_validate(data)

        assert task.parent is not None
        assert task.parent.gid == "task1"
        assert task.parent.name == "Parent Task"


class TestTaskRequestModels:
    """Tests for task request models."""

    def test_task_create_request(self):
        """Test TaskCreateRequest model."""
        request = TaskCreateRequest(
            name="New Task",
            workspace="ws1",
            projects=["proj1"],
            assignee="me",
            due_on=date(2024, 7, 1),
            notes="Task notes",
        )

        data = request.model_dump(exclude_none=True)
        assert data["name"] == "New Task"
        assert data["workspace"] == "ws1"
        assert data["projects"] == ["proj1"]
        assert data["assignee"] == "me"
        assert data["due_on"] == date(2024, 7, 1)

    def test_task_create_minimal(self):
        """Test TaskCreateRequest with minimal fields."""
        request = TaskCreateRequest(name="Simple Task")
        data = request.model_dump(exclude_none=True)

        assert data["name"] == "Simple Task"
        assert "workspace" not in data
        assert "projects" not in data

    def test_task_update_request(self):
        """Test TaskUpdateRequest model."""
        request = TaskUpdateRequest(
            name="Updated Name",
            completed=True,
        )

        data = request.model_dump(exclude_none=True)
        assert data["name"] == "Updated Name"
        assert data["completed"] is True
        assert "assignee" not in data

    def test_task_update_partial(self):
        """Test TaskUpdateRequest allows partial updates."""
        request = TaskUpdateRequest(completed=True)
        data = request.model_dump(exclude_none=True)

        assert data == {"completed": True}
