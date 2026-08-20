# 🚀 Job Tracker API

A secure RESTful API for managing job applications, built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **JWT Authentication**, **Alembic**, and **Pytest**.

---

# ✨ Features

- User Registration
- JWT Authentication
- Password Hashing using bcrypt
- User Authorization (Users can only access their own job applications)
- Complete CRUD Operations
- Partial Updates (PATCH)
- Job Filtering
- Job Sorting
- Pagination
- Health Check Endpoint
- Automatic `created_at` & `updated_at` timestamps
- Alembic Database Migrations
- Automated API Testing using Pytest
- PostgreSQL Database Integration
- Interactive Swagger API Documentation

---

# 📸 Screenshots

## Swagger Documentation

![Swagger Home](images/swagger-home.png)

---

## User Registration

![Register](images/register-success.png)

---

## User Login

![Login](images/login-success.png)

---

## JWT Authorization

![JWT Authorization](images/authorize-jwt.png)

---

## Get Jobs

![Jobs Endpoint](images/jobs-endpoint.png)

---

## Partial Update (PATCH)

![Patch Job](images/patch-job.png)

---

## Health Endpoint

![Health Endpoint](images/health-endpoint.png)

---

## Automated Testing

![Pytest Results](images/pytest-results.png)

---

# 🛠 Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT (python-jose)
- bcrypt
- Pytest
- python-dotenv
- Uvicorn

---

# 📁 Project Structure

```text
JobTrackerAPI/
│
├── alembic/
│   └── versions/
│
├── images/
│
├── tests/
│   ├── conftest.py
│   └── test_main.py
│
├── auth.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── security.py
├── requirements.txt
├── alembic.ini
├── README.md
├── LICENSE
├── .env.example
└── .gitignore
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/shravis/job-tracker-api.git

cd job-tracker-api

```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

---

## 3. Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Create the PostgreSQL database

Do not skip this step. Alembic cannot create the database itself.

```bash
createdb job_tracker
```

Create a dedicated role instead of using the `postgres` superuser:

```bash
createuser jobtracker
createdb -O jobtracker job_tracker
```

For tests:

```bash
createdb -O jobtracker job_tracker_test
```

---

## 6. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values.

```env
DATABASE_URL=postgresql://jobtracker:your_password@localhost:5432/job_tracker

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_MINUTES=10080

ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

TRUST_PROXY=false
```

If the API sits behind a reverse proxy, set `TRUST_PROXY=true` **and** start Uvicorn with `--forwarded-allow-ips` set to that proxy's address only. Leave `TRUST_PROXY=false` for local development.

Rate limits are stored in the current process. Each extra Uvicorn worker has its own counter, so do not scale workers until you add a shared store.

---

## 7. Apply Database Migrations

Schema changes come **only** from Alembic (the app no longer calls `create_all` on startup).

If you already have a `job_tracker` database from an older version, still run this. The repair migration adds `user_id`, indexes, and cleans invalid `status` values.

```bash
alembic upgrade head
```

---

## 8. Run the Application

```bash
uvicorn main:app --reload --no-proxy-headers
```

`--no-proxy-headers` stops Uvicorn from treating `X-Forwarded-For` as the client IP on localhost (which would bypass rate limiting).

Behind a real proxy:

```bash
uvicorn main:app --forwarded-allow-ips=10.0.0.1
```

and set `TRUST_PROXY=true`.

---

# 📖 API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

OpenAPI JSON

```
http://127.0.0.1:8000/openapi.json
```

---

# 🔐 Authentication Flow

1. Register a new user.
2. Login using your username and password.
3. Receive a JWT access token.
4. Click **Authorize** in Swagger.
5. Paste the access token.
6. Access protected endpoints.
7. Users can only access their own job applications.

---

# 📌 Available Endpoints

## Authentication

- POST `/register`
- POST `/login`
- POST `/refresh`
- POST `/logout`

### Jobs

- GET `/jobs`
- GET `/jobs/{job_id}`
- POST `/jobs`
- PUT `/jobs/{job_id}`
- PATCH `/jobs/{job_id}`
- DELETE `/jobs/{job_id}`

### System

- GET `/`
- GET `/about`
- GET `/health`

---

# 🧪 Running Tests

Run the automated test suite:

```bash
# Required if DATABASE_URL points at a non-test database (the suite will refuse it).
set TEST_DATABASE_URL=postgresql://jobtracker:your_password@localhost:5432/job_tracker_test

pytest -v
```

The test database name must contain `test`. The suite never runs `drop_all` against `job_tracker`.

### Current Test Coverage

- Home Endpoint
- About Endpoint
- User Registration
- User Login
- Create Job
- Get Jobs
- Patch Job
- Delete Job
- Unauthorized Access
- Health Endpoint
- Job Status DB-Level CHECK Constraint (ensures invalid status values are rejected even if the API/schema layer is bypassed)

---

# 🚀 Future Improvements

- Email Notifications
- Resume Uploads
- Company Search
- Job Analytics Dashboard
- Docker Support
- CI/CD Pipeline

---

# 👩‍💻 Author

**Shravya**

Designed and developed a secure RESTful API for managing job applications using FastAPI, PostgreSQL, SQLAlchemy, JWT Authentication, Alembic, and Pytest.