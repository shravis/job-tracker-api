from fastapi.testclient import TestClient


def test_home(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Job Tracker API"
    }


def test_about(client: TestClient):
    response = client.get("/about")

    assert response.status_code == 200
    assert response.json() == {
        "developer": "Shravya"
    }


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

    job = response.json()

    assert job["company"] == "Google"
    assert job["status"] == "Applied"


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