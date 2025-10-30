# Backend Service

The FastAPI backend exposes REST endpoints for running AI-generated media detection.

## Endpoints

- `POST /detect/image`: Accepts an image upload and returns a probability that the content is synthetic.
- `POST /detect/video`: Accepts a video upload, samples frames, and aggregates frame-level predictions.
- `GET /health`: Basic readiness probe with model metadata.

## Running Locally

```bash
uvicorn app.main:app --reload
```

The service persists detection results in SQLite by default (`backend/app.db`). Configure settings via environment variables. See `app/config.py` for available options.
