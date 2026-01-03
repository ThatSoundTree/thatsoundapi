from typing import Any, cast

from fastapi import status
from loguru import logger

from thatsoundapi.core.exceptions import BadRequestError, UnauthorizedError
from thatsoundapi.settings import get_settings
from thatsoundapi.utils.http_client import TSDirectHTTPClient


class TaskService:
    """Service for interacting with TSDirect task API."""

    @staticmethod
    async def create_task(task_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task in TSDirect."""
        settings = get_settings()
        url = f"{settings.TSDIRECT_API_BASE_URL}/tasks"

        response = await TSDirectHTTPClient.post(url, json=task_data)

        if response.status_code == 401:
            logger.error("TSDirect API authentication failed")
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "TSDirect API authentication failed")

        if response.status_code not in (200, 201):
            error_text = response.text[:200]
            logger.error(
                "Failed to create task",
                status_code=response.status_code,
                error=error_text,
            )
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Failed to create task in TSDirect")

        return cast(dict[str, Any], response.json())

    @staticmethod
    async def get_task(task_id: str) -> dict[str, Any]:
        """Get a task by ID from TSDirect."""
        settings = get_settings()
        url = f"{settings.TSDIRECT_API_BASE_URL}/tasks/{task_id}"

        response = await TSDirectHTTPClient.get(url)

        if response.status_code == 401:
            logger.error("TSDirect API authentication failed")
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "TSDirect API authentication failed")

        if response.status_code == 404:
            logger.warning("Task not found", task_id=task_id)
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Task not found")

        if response.status_code != 200:
            error_text = response.text[:200]
            logger.error(
                "Failed to get task",
                status_code=response.status_code,
                error=error_text,
            )
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Failed to get task from TSDirect")

        return cast(dict[str, Any], response.json())

    @staticmethod
    async def update_task(task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Update a task in TSDirect."""
        settings = get_settings()
        url = f"{settings.TSDIRECT_API_BASE_URL}/tasks/{task_id}"

        response = await TSDirectHTTPClient.put(url, json=task_data)

        if response.status_code == 401:
            logger.error("TSDirect API authentication failed")
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "TSDirect API authentication failed")

        if response.status_code == 404:
            logger.warning("Task not found", task_id=task_id)
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Task not found")

        if response.status_code != 200:
            error_text = response.text[:200]
            logger.error(
                "Failed to update task",
                status_code=response.status_code,
                error=error_text,
            )
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Failed to update task in TSDirect")

        return cast(dict[str, Any], response.json())

    @staticmethod
    async def delete_task(task_id: str) -> None:
        """Delete a task from TSDirect."""
        settings = get_settings()
        url = f"{settings.TSDIRECT_API_BASE_URL}/tasks/{task_id}"

        response = await TSDirectHTTPClient.delete(url)

        if response.status_code == 401:
            logger.error("TSDirect API authentication failed")
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "TSDirect API authentication failed")

        if response.status_code == 404:
            logger.warning("Task not found", task_id=task_id)
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Task not found")

        if response.status_code not in (200, 204):
            error_text = response.text[:200]
            logger.error(
                "Failed to delete task",
                status_code=response.status_code,
                error=error_text,
            )
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Failed to delete task from TSDirect")

    @staticmethod
    async def list_tasks(**params: Any) -> list[dict[str, Any]]:
        """List tasks from TSDirect."""
        settings = get_settings()
        url = f"{settings.TSDIRECT_API_BASE_URL}/tasks"

        response = await TSDirectHTTPClient.get(url, params=params)

        if response.status_code == 401:
            logger.error("TSDirect API authentication failed")
            raise UnauthorizedError(status.HTTP_401_UNAUTHORIZED, "TSDirect API authentication failed")

        if response.status_code != 200:
            error_text = response.text[:200]
            logger.error(
                "Failed to list tasks",
                status_code=response.status_code,
                error=error_text,
            )
            raise BadRequestError(status.HTTP_400_BAD_REQUEST, "Failed to list tasks from TSDirect")

        result = response.json()
        # Handle both list and dict with 'items' key
        if isinstance(result, list):
            return cast(list[dict[str, Any]], result)
        elif isinstance(result, dict) and "items" in result:
            items = result["items"]
            if isinstance(items, list):
                return cast(list[dict[str, Any]], items)
        return []
