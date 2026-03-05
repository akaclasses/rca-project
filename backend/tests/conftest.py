"""Fixtures partagées pour les tests pytest."""

import pytest

from model import Task


@pytest.fixture
def sample_task() -> Task:
    """Retourne une tâche exemple pour les tests."""
    from datetime import datetime, timezone

    return Task(
        id=1,
        title="Test task",
        description="A test description",
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_task_data() -> dict:
    """Retourne les données JSON pour créer une tâche."""
    return {"title": "New task", "description": "Some description"}
