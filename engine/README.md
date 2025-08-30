# Hiresify Engine

Hiresify Engine is a backend service built with **FastAPI**.  
It provides authentication, user management, resumable file uploads, and a clean
service-oriented architecture ready for production.

---

## Features

- **Authentication**
  - OAuth2 with PKCE and JWT
  - Secure password hashing
- **User Management**
  - Signup, login, refresh tokens
- **Blob Storage**
  - Multipart / chunked uploads
  - Pause & resume support
- **Database Layer**
  - Async SQLAlchemy models & repositories
  - Exception handling & mapping
- **Caching**
  - Abstraction for Redis or in-memory cache
- **Testing**
  - Full pytest suite with fixtures
  - Mock DB/cache helpers

---

## Project Structure

```
engine/
├── pyproject.toml          # Dependencies & build config
├── uv.lock                 # Lock file
├── src/hiresify_engine/
│   ├── app/                # FastAPI app setup
│   ├── router/             # API endpoints (user, token, blob, util)
│   ├── service/            # Business logic
│   ├── db/                 # Database models & repositories
│   ├── dep/                # Dependency injection
│   ├── tool/               # Utilities (PKCE, password, etc.)
│   ├── testing/            # Test fixtures & data
│   ├── model/              # Pydantic schemas
│   ├── config.py           # Settings
│   └── const.py            # Constants
```

---

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/your-username/hiresify-engine.git
cd hiresify-engine/engine
uv sync   # or: pip install -e .
```

### 2. Configure

Create a `.env` file (or set environment variables):

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hiresify
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

### 3. Run

```bash
uvicorn hiresify_engine.app.main:app --reload
```

Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Overview

| Endpoint               | Method | Description              |
|------------------------|--------|--------------------------|
| `/user/signup`         | POST   | Register new user        |
| `/user/login`          | POST   | Authenticate & get token |
| `/token/refresh`       | POST   | Refresh access token     |
| `/blob/upload/init`    | POST   | Initialize upload        |
| `/blob/upload/chunk`   | POST   | Upload a chunk           |
| `/blob/upload/complete`| POST   | Finalize upload          |
| `/util/ping`           | GET    | Health check             |

---

## Testing

```bash
pytest
```

---

## License

MIT. See [LICENSE](../LICENSE).
