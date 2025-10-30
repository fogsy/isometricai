# Deployment & Operations Guide

This document outlines how to configure and deploy the AI Media Authenticity Detector.

## 1. Prerequisites

- **Python 3.10+** with `pip`.
- **Node.js 18+** with `npm` or `yarn`.
- Optional: **CUDA-capable GPU** for accelerated inference.

## 2. Backend Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Configure environment variables (see `backend/app/config.py`).
4. Initialize the database (SQLite by default):
   ```bash
   uvicorn app.main:app --reload
   ```
   The service auto-creates tables on startup.

## 3. Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
3. Set the `VITE_API_BASE_URL` environment variable to the backend URL if different from the default `http://localhost:8000`.

## 4. Evaluation Toolkit

The scripts under `tools/eval/` allow batch evaluation of datasets of real vs. synthetic media. See `tools/eval/README.md` for details.

## 5. Production Deployment

- Use a process manager such as `uvicorn` with `gunicorn` workers or Docker.
- Configure CORS and HTTPS termination via a reverse proxy (Nginx, Traefik, etc.).
- Set up centralized logging (e.g., ELK, Loki) and metrics scraping (Prometheus) for observability.

## 6. Continuous Integration

A sample GitHub Actions workflow is provided in `.github/workflows/ci.yml` to run linting, unit tests, and evaluation smoke tests.
