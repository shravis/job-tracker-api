# 🚀 Job Tracker API

A secure RESTful API built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **JWT Authentication** to help users manage and track job applications.

---

# Features

- User Registration
- User Login using JWT Authentication
- Password Hashing with bcrypt
- Protected CRUD Operations
- Job Filtering
- Job Sorting
- Pagination
- PostgreSQL Database Integration
- Interactive Swagger API Documentation

---

# Screenshots

## Swagger Documentation

![Swagger Home](images/swagger-home.png)

---

## User Registration

![Register](images/register-success.png)

---

## User Login (JWT Authentication)

![Login](images/login-success.png)

---

## Protected Jobs Endpoint

![Jobs Endpoint](images/jobs-endpoint.png)

---

# Tech Stack

- Python 3
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT (python-jose)
- Passlib (bcrypt)
- Uvicorn
- python-dotenv

---

# Project Structure

```
JobTrackerAPI/
│
├── auth.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── security.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/job-tracker-api.git
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

## 5. Configure environment variables

Create a `.env` file using the `.env.example` template.

Example:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/job_tracker

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 6. Start the server

```bash
uvicorn main:app --reload
```

---

# API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

OpenAPI JSON

```
http://127.0.0.1:8000/openapi.json
```

---

# Authentication Flow

1. Register a new user.
2. Login using your username and password.
3. Receive a JWT access token.
4. Authorize in Swagger.
5. Access protected endpoints.

---

# Available Endpoints

## Authentication

- POST `/register`
- POST `/login`

## Jobs

- GET `/jobs`
- GET `/jobs/{job_id}`
- POST `/jobs`
- PUT `/jobs/{job_id}`
- DELETE `/jobs/{job_id}`

---

# Author

Developed by **Shravya**
