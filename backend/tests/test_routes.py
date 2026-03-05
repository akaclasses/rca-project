"""Tests unitaires pour les routes de l'application Flask."""

import json
import os
import sys
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("DATABASE_URL", "postgres://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# Mock les modules qui ne sont pas installés localement
sys.modules.setdefault("psycopg2", MagicMock())
sys.modules.setdefault("psycopg2.extras", MagicMock())
sys.modules.setdefault("redis", MagicMock())

from app import app  # noqa: E402


@pytest.fixture
def client():
    """Crée un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_endpoint(client) -> None:
    """Vérifie que /health retourne un status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_create_task_missing_title(client) -> None:
    """Vérifie qu'une erreur 400 est retournée sans titre."""
    response = client.post(
        "/api/tasks",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_create_task_empty_body(client) -> None:
    """Vérifie qu'une erreur 400 est retournée avec un body vide."""
    response = client.post("/api/tasks", content_type="application/json")
    assert response.status_code == 400
