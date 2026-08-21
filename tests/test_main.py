from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

import models

import pytest


def test_home(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Job Tracker API"
    }


def test_about(client: TestClient):
    response = client.get("/about")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Job Tracker API"
    assert data["author"] == "Shravya"
    assert "version" in data


def test_register_user(client: TestClient):
    response = client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    assert response.status_code == 201


def test_login_user(client: TestClient):
    client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "john",
            "password": "Password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_job(client: TestClient):
    client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    login = client.post(
        "/login",
        data={
            "username": "john",
            "password": "Password123"
        }
    )

    token = login.json()["access_token"]

    response = client.post(
        "/jobs",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "company": "Google",
            "position": "Software Engineer",
            "status": "Applied"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Google"
    assert data["position"] == "Software Engineer"
    assert data["status"] == "Applied"


def test_patch_job(client: TestClient):
    client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    login = client.post(
        "/login",
        data={
            "username": "john",
            "password": "Password123"
        }
    )

    token = login.json()["access_token"]

    job = client.post(
        "/jobs",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "company": "Google",
            "position": "Software Engineer",
            "status": "Applied"
        }
    )

    job_id = job.json()["id"]

    response = client.patch(
        f"/jobs/{job_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "Interview"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Interview"


def test_delete_job(client: TestClient):
    client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    login = client.post(
        "/login",
        data={
            "username": "john",
            "password": "Password123"
        }
    )

    token = login.json()["access_token"]

    job = client.post(
        "/jobs",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "company": "Google",
            "position": "Software Engineer",
            "status": "Applied"
        }
    )

    job_id = job.json()["id"]

    response = client.delete(
        f"/jobs/{job_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 204


def test_get_jobs(client: TestClient):
    client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    login = client.post(
        "/login",
        data={
            "username": "john",
            "password": "Password123"
        }
    )

    token = login.json()["access_token"]

    client.post(
        "/jobs",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "company": "Google",
            "position": "Software Engineer",
            "status": "Applied"
        }
    )

    response = client.get(
        "/jobs",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_health(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected"
    }


def test_unauthorized_access(client: TestClient):
    response = client.get("/jobs")

    assert response.status_code == 401


def test_job_ownership_isolation(client: TestClient):
    client.post(
        "/register",
        json={"username": "alice", "password": "Password123"}
    )
    client.post(
        "/register",
        json={"username": "bob", "password": "Password123"}
    )

    token_a = client.post(
        "/login",
        data={"username": "alice", "password": "Password123"}
    ).json()["access_token"]
    token_b = client.post(
        "/login",
        data={"username": "bob", "password": "Password123"}
    ).json()["access_token"]

    created = client.post(
        "/jobs",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "company": "Google",
            "position": "Software Engineer",
            "status": "Applied"
        }
    )
    assert created.status_code == 201
    job_id = created.json()["id"]

    headers_b = {"Authorization": f"Bearer {token_b}"}

    assert client.get(f"/jobs/{job_id}", headers=headers_b).status_code == 404
    assert client.put(
        f"/jobs/{job_id}",
        headers=headers_b,
        json={
            "company": "Evil",
            "position": "Hacker",
            "status": "Offer"
        }
    ).status_code == 404
    assert client.patch(
        f"/jobs/{job_id}",
        headers=headers_b,
        json={"status": "Rejected"}
    ).status_code == 404
    assert client.delete(
        f"/jobs/{job_id}",
        headers=headers_b
    ).status_code == 404
    assert client.get("/jobs", headers=headers_b).json() == []

    kept = client.get(
        f"/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert kept.status_code == 200
    assert kept.json()["company"] == "Google"


def test_db_rejects_invalid_status_via_check_constraint(
    client: TestClient,
    db_session
):
    """schemas.JobStatus already blocks bad statuses at the API layer.
    This proves the DB itself enforces the same rule (ck_jobs_status),
    so a bad value inserted via raw SQL / a future code path that
    skips Pydantic still can't corrupt the table (regression guard
    for the case-sensitive NOT IN bug the migration fixed)."""
    client.post(
        "/register",
        json={
            "username": "john",
            "password": "Password123"
        }
    )

    user = db_session.query(models.User).filter(
        models.User.username == "john"
    ).first()

    bad_job = models.Job(
        company="Google",
        position="Software Engineer",
        status="not-a-real-status",
        user_id=user.id
    )
    db_session.add(bad_job)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()