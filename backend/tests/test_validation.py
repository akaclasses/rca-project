"""Tests pour la validation des données d'entrée."""

import json
import os
import sys
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("DATABASE_URL", "postgres://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

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


def test_create_task_no_json(client) -> None:
    """Vérifie le rejet d'une requête sans Content-Type JSON."""
    response = client.post("/api/tasks", data="not json")
    assert response.status_code in (400, 415)


def test_create_task_title_empty_string(client) -> None:
    """Vérifie le rejet d'un titre vide."""
    response = client.post(
        "/api/tasks",
        data=json.dumps({"title": ""}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_health_returns_json(client) -> None:
    """Vérifie que /health retourne du JSON valide."""
    response = client.get("/health")
    assert response.content_type == "application/json"
