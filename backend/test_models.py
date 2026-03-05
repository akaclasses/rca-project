import pytest
from datetime import datetime, timezone
from models import Task

def test_task_creation():
    now = datetime.now(timezone.utc)
    task = Task(id=1, title="Test Task", description="Testing", is_active=True, created_at=now)
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.is_active is True

def test_task_to_dict():
    now = datetime.now(timezone.utc)
    task = Task(id=2, title="Dict Task", description="", is_active=False, created_at=now)
    data = task.to_dict()
    assert data["id"] == 2
    assert data["title"] == "Dict Task"
    assert data["is_active"] is False
    assert "created_at" in data
