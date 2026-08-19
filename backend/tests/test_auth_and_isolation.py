from tests.conftest import auth_headers, register_org


def test_register_and_login(client):
    result = register_org(client)
    assert result["user"]["role"] == "org_admin"
    assert "access_token" in result

    login = client.post("/auth/login", json={"email": "admin@testorg.com", "password": "TestPass123!"})
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "admin@testorg.com"


def test_login_wrong_password_rejected(client):
    register_org(client)
    login = client.post("/auth/login", json={"email": "admin@testorg.com", "password": "wrong-password"})
    assert login.status_code == 401


def test_duplicate_email_registration_rejected(client):
    register_org(client)
    response = client.post(
        "/auth/register",
        json={
            "name": "Another Admin",
            "email": "admin@testorg.com",
            "password": "AnotherPass123!",
            "organisation": {"name": "Another Org", "sector": "healthcare"},
            "language": "en",
        },
    )
    assert response.status_code == 409


def test_organisation_isolation_blocks_cross_org_access(client):
    org_a = register_org(client, name="Org A", email="a@orga.com")
    org_b = register_org(client, name="Org B", email="b@orgb.com")

    # Org A starts an assessment
    start = client.post(
        "/assessments/start",
        json={"sector": "finance", "role": "it_administrator", "language": "en"},
        headers=auth_headers(org_a["access_token"]),
    )
    assert start.status_code == 200
    assessment_id = start.json()["id"]

    # Org B must not be able to read Org A's assessment
    blocked = client.get(f"/assessments/{assessment_id}", headers=auth_headers(org_b["access_token"]))
    assert blocked.status_code == 403


def test_unauthenticated_request_rejected(client):
    response = client.get("/organisations/me")
    assert response.status_code == 401
