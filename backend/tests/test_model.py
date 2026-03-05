"""Tests unitaires pour le modèle Task."""

from datetime import datetime, timezone

from model import Task


def test_task_creation() -> None:
    """Vérifie la création d'une instance Task."""
    task = Task(
        id=1,
        title="Test",
        description="Desc",
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert task.id == 1
    assert task.title == "Test"
    assert task.is_active is True


def test_task_to_dict() -> None:
    """Vérifie la sérialisation d'une Task en dictionnaire."""
    dt = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    task = Task(
        id=2,
        title="Dict test",
        description="Desc",
        is_active=False,
        created_at=dt,
        updated_at=dt,
    )
    d = task.to_dict()
    assert d["id"] == 2
    assert d["title"] == "Dict test"
    assert d["is_active"] is False
    assert d["created_at"] == dt.isoformat()
    assert d["updated_at"] == dt.isoformat()


def test_task_to_dict_none_updated_at() -> None:
    """Vérifie que updated_at=None est sérialisé correctement."""
    task = Task(
        id=3,
        title="No update",
        description="",
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=None,
    )
    d = task.to_dict()
    assert d["updated_at"] is None


def test_task_default_updated_at() -> None:
    """Vérifie la valeur par défaut de updated_at."""
    task = Task(
        id=4,
        title="Default",
        description="",
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert task.updated_at is None
