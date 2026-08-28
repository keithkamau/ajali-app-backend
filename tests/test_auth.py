import pytest


@pytest.fixture
def reg_payload():
    return {
        "email": "newuser@example.com",
        "password": "secret123",
        "full_name": "New User",
        "phone_number": "+254711000000",
    }


def test_register_success(client, reg_payload):
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == reg_payload["email"]
    assert "password_hash" not in data["user"]


def test_register_duplicate_email(client, reg_payload):
    client.post("/api/auth/register", json=reg_payload)
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 409
    assert "already registered" in res.get_json()["error"]


def test_register_missing_required_fields(client):
    res = client.post("/api/auth/register", json={"email": "x@x.com"})
    assert res.status_code == 400
    assert "errors" in res.get_json()


def test_register_short_password(client):
    res = client.post("/api/auth/register", json={
        "email": "short@x.com",
        "password": "abc",
        "full_name": "Short Pass",
    })
    assert res.status_code == 400


def test_login_success(client, reg_payload):
    client.post("/api/auth/register", json=reg_payload)
    res = client.post("/api/auth/login", json={
        "email": reg_payload["email"],
        "password": reg_payload["password"],
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, reg_payload):
    client.post("/api/auth/register", json=reg_payload)
    res = client.post("/api/auth/login", json={
        "email": reg_payload["email"],
        "password": "wrongpassword",
    })
    assert res.status_code == 401
    assert "Invalid" in res.get_json()["error"]


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "anything",
    })
    assert res.status_code == 401


def test_login_missing_fields(client):
    res = client.post("/api/auth/login", json={"email": "x@x.com"})
    assert res.status_code == 400


def test_refresh_returns_new_access_token(client, reg_payload):
    reg = client.post("/api/auth/register", json=reg_payload).get_json()
    refresh_token = reg["refresh_token"]
    res = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_me_returns_current_user(client, reg_payload):
    reg = client.post("/api/auth/register", json=reg_payload).get_json()
    access_token = reg["access_token"]
    res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert res.status_code == 200
    assert res.get_json()["user"]["email"] == reg_payload["email"]
