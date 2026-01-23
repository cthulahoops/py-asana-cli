"""Base Asana API client with httpx."""

from collections.abc import Iterator
from typing import Any

import httpx

from asana_cli.client.exceptions import (
    AsanaAPIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from asana_cli.config import get_token


class AsanaClient:
    """Base client for Asana API."""

    BASE_URL = "https://app.asana.com/api/1.0"

    def __init__(self, token: str | None = None):
        """Initialize the client with an optional token override."""
        self._token = token or get_token()
        if not self._token:
            raise ConfigurationError(
                "No API token configured. Run 'asana config set-token <token>' "
                "or set ASANA_TOKEN environment variable."
            )
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "AsanaClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        status_code = response.status_code

        try:
            error_data = response.json()
            errors = error_data.get("errors", [])
            message = errors[0].get("message", "Unknown error") if errors else "Unknown error"
        except Exception:
            message = response.text or "Unknown error"

        if status_code == 401:
            raise AuthenticationError(message, status_code)
        elif status_code == 404:
            raise NotFoundError(message, status_code)
        elif status_code == 429:
            raise RateLimitError(message, status_code)
        elif status_code == 400:
            raise ValidationError(message, status_code)
        else:
            raise AsanaAPIError(message, status_code)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        opt_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        params = params or {}

        if opt_fields:
            params["opt_fields"] = ",".join(opt_fields)

        response = self._client.request(method, path, params=params, json=json)

        if not response.is_success:
            self._handle_error(response)

        return response.json()

    def _paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        opt_fields: list[str] | None = None,
        limit: int = 100,
    ) -> Iterator[dict[str, Any]]:
        """Paginate through API results."""
        params = params or {}
        params["limit"] = limit

        if opt_fields:
            params["opt_fields"] = ",".join(opt_fields)

        while True:
            response = self._client.get(path, params=params)

            if not response.is_success:
                self._handle_error(response)

            data = response.json()
            yield from data.get("data", [])

            next_page = data.get("next_page")
            if not next_page:
                break

            params["offset"] = next_page["offset"]

    # User endpoints
    def get_me(self, opt_fields: list[str] | None = None) -> dict[str, Any]:
        """Get the current user."""
        response = self._request("GET", "/users/me", opt_fields=opt_fields)
        return response["data"]

    def get_user(self, user_gid: str, opt_fields: list[str] | None = None) -> dict[str, Any]:
        """Get a user by GID."""
        response = self._request("GET", f"/users/{user_gid}", opt_fields=opt_fields)
        return response["data"]

    # Workspace endpoints
    def get_workspaces(self, opt_fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Get all workspaces for the current user."""
        return list(self._paginate("/workspaces", opt_fields=opt_fields))

    # Project endpoints
    def get_projects(
        self,
        workspace: str,
        archived: bool = False,
        opt_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get projects in a workspace."""
        params = {"workspace": workspace, "archived": str(archived).lower()}
        return list(self._paginate("/projects", params=params, opt_fields=opt_fields))

    def get_project(self, project_gid: str, opt_fields: list[str] | None = None) -> dict[str, Any]:
        """Get a project by GID."""
        response = self._request("GET", f"/projects/{project_gid}", opt_fields=opt_fields)
        return response["data"]

    # Section endpoints
    def get_sections(
        self, project_gid: str, opt_fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get sections in a project."""
        return list(
            self._paginate(f"/projects/{project_gid}/sections", opt_fields=opt_fields)
        )

    def get_section_tasks(
        self, section_gid: str, opt_fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get tasks in a section."""
        return list(self._paginate(f"/sections/{section_gid}/tasks", opt_fields=opt_fields))

    # Task endpoints
    def get_tasks(
        self,
        project: str | None = None,
        section: str | None = None,
        assignee: str | None = None,
        workspace: str | None = None,
        completed_since: str | None = None,
        opt_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Get tasks with optional filters."""
        params: dict[str, Any] = {}

        if project:
            params["project"] = project
        if section:
            params["section"] = section
        if assignee:
            params["assignee"] = assignee
            if workspace:
                params["workspace"] = workspace
        if completed_since:
            params["completed_since"] = completed_since

        return list(self._paginate("/tasks", params=params, opt_fields=opt_fields))

    def get_task(self, task_gid: str, opt_fields: list[str] | None = None) -> dict[str, Any]:
        """Get a task by GID."""
        response = self._request("GET", f"/tasks/{task_gid}", opt_fields=opt_fields)
        return response["data"]

    def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task."""
        response = self._request("POST", "/tasks", json={"data": data})
        return response["data"]

    def update_task(self, task_gid: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a task."""
        response = self._request("PUT", f"/tasks/{task_gid}", json={"data": data})
        return response["data"]

    def get_subtasks(
        self, task_gid: str, opt_fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get subtasks of a task."""
        return list(self._paginate(f"/tasks/{task_gid}/subtasks", opt_fields=opt_fields))

    def create_subtask(self, parent_gid: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a subtask under a parent task."""
        response = self._request("POST", f"/tasks/{parent_gid}/subtasks", json={"data": data})
        return response["data"]

    def add_task_to_section(self, section_gid: str, task_gid: str) -> None:
        """Move a task to a section."""
        self._request(
            "POST",
            f"/sections/{section_gid}/addTask",
            json={"data": {"task": task_gid}},
        )

    def delete_task(self, task_gid: str) -> None:
        """Delete a task."""
        self._request("DELETE", f"/tasks/{task_gid}")
