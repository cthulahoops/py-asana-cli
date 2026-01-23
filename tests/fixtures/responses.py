"""Test fixture data for Asana API responses."""

USER_ME = {
    "data": {
        "gid": "12345",
        "name": "Test User",
        "email": "test@example.com",
        "resource_type": "user",
        "workspaces": [
            {"gid": "workspace1", "name": "Workspace One"},
            {"gid": "workspace2", "name": "Workspace Two"},
        ],
    }
}

USER_DETAIL = {
    "data": {
        "gid": "67890",
        "name": "Other User",
        "email": "other@example.com",
        "resource_type": "user",
        "workspaces": [{"gid": "workspace1", "name": "Workspace One"}],
    }
}

WORKSPACES = {
    "data": [
        {"gid": "workspace1", "name": "Workspace One"},
        {"gid": "workspace2", "name": "Workspace Two"},
    ],
    "next_page": None,
}

PROJECTS = {
    "data": [
        {
            "gid": "project1",
            "name": "Project One",
            "archived": False,
            "owner": {"gid": "12345", "name": "Test User"},
        },
        {
            "gid": "project2",
            "name": "Project Two",
            "archived": True,
            "owner": {"gid": "12345", "name": "Test User"},
        },
    ],
    "next_page": None,
}

PROJECT_DETAIL = {
    "data": {
        "gid": "project1",
        "name": "Project One",
        "notes": "Project description",
        "archived": False,
        "owner": {"gid": "12345", "name": "Test User"},
        "workspace": {"gid": "workspace1", "name": "Workspace One"},
        "created_at": "2024-01-01T00:00:00.000Z",
        "due_on": "2024-12-31",
        "start_on": "2024-01-01",
    }
}

SECTIONS = {
    "data": [
        {"gid": "section1", "name": "To Do", "created_at": "2024-01-01T00:00:00.000Z"},
        {"gid": "section2", "name": "In Progress", "created_at": "2024-01-01T00:00:00.000Z"},
        {"gid": "section3", "name": "Done", "created_at": "2024-01-01T00:00:00.000Z"},
    ],
    "next_page": None,
}

TASKS = {
    "data": [
        {
            "gid": "task1",
            "name": "Task One",
            "completed": False,
            "due_on": "2024-06-01",
            "assignee": {"gid": "12345", "name": "Test User"},
            "num_subtasks": 2,
        },
        {
            "gid": "task2",
            "name": "Task Two",
            "completed": True,
            "due_on": None,
            "assignee": None,
            "num_subtasks": 0,
        },
    ],
    "next_page": None,
}

TASK_DETAIL = {
    "data": {
        "gid": "task1",
        "name": "Task One",
        "notes": "Task description here",
        "completed": False,
        "completed_at": None,
        "created_at": "2024-01-15T10:00:00.000Z",
        "due_on": "2024-06-01",
        "due_at": None,
        "assignee": {"gid": "12345", "name": "Test User"},
        "projects": [{"gid": "project1", "name": "Project One"}],
        "parent": None,
        "num_subtasks": 2,
        "permalink_url": "https://app.asana.com/0/project1/task1",
    }
}

SUBTASKS = {
    "data": [
        {
            "gid": "subtask1",
            "name": "Subtask One",
            "completed": False,
            "due_on": None,
            "assignee": None,
        },
        {
            "gid": "subtask2",
            "name": "Subtask Two",
            "completed": True,
            "due_on": "2024-05-01",
            "assignee": {"gid": "12345", "name": "Test User"},
        },
    ],
    "next_page": None,
}

TASK_CREATED = {
    "data": {
        "gid": "newtask",
        "name": "New Task",
        "completed": False,
        "due_on": "2024-07-01",
        "assignee": {"gid": "12345", "name": "Test User"},
    }
}

TASK_UPDATED = {
    "data": {
        "gid": "task1",
        "name": "Task One Updated",
        "completed": True,
    }
}

ERROR_NOT_FOUND = {"errors": [{"message": "Resource not found", "help": "Check the GID"}]}

ERROR_UNAUTHORIZED = {"errors": [{"message": "Not authorized", "help": "Check your token"}]}
