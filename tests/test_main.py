import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "broadcmo-api-gateway"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Broadcmo" in data["message"]


def test_unknown_service_returns_404():
    response = client.get("/servicio-inexistente/endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "no encontrado" in data["detail"]


def test_health_response_has_version():
    response = client.get("/health")
    assert response.status_code == 200
    assert "version" in response.json()
