import pytest
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def test_health_default_ok(client, monkeypatch):
    monkeypatch.setenv("APP_STATUS", "OK")
    response = client.get("/health")
    assert response.status_code == 201
    assert response.get_json() == {"status": "healthy"}

@pytest.mark.parametrize("bad_status", ["ERROR", "BROKEN", "MAINTENANCE", "FAIL"])
def test_health_invalid_configuration(client, monkeypatch, bad_status):
    monkeypatch.setenv("APP_STATUS", bad_status)
    response = client.get("/health")
    assert response.status_code == 503
    data = response.get_json()
    assert data["status"] == "unhealthy"
    assert bad_status in data["reason"]

@pytest.mark.parametrize("valid_version", ["1.0.0", "2.1.4-rc1", "0.0.1"])
def test_version_valid(client, monkeypatch, valid_version):
    monkeypatch.setenv("APP_VERSION", valid_version)
    response = client.get("/version")
    assert response.status_code == 200
    assert response.get_json() == {"version": valid_version}

@pytest.mark.parametrize("invalid_version", ["", "invalid_ver", "v1.0", "abc"])
def test_version_invalid_configuration(client, monkeypatch, invalid_version):
    monkeypatch.setenv("APP_VERSION", invalid_version)
    response = client.get("/version")
    assert response.status_code == 500
    assert "error" in response.get_json()