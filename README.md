# Cost Estimator

Cost Estimator is a FastAPI-based backend application that generates structured cost estimation reports using an LLM and exports them as Excel or PDF files.

## Features
- REST API for cost estimation requests
- LLM-powered response generation for project estimates
- Excel and PDF report generation
- CORS-enabled backend for frontend integration

## Project structure
- backend/app: FastAPI application and services
- backend/app/router: API routes
- backend/app/services: document, PDF, Excel, and LLM services

## Setup
1. Create and activate a virtual environment
   - Windows PowerShell:
     - `python -m venv .venv`
     - `./.venv/Scripts/Activate.ps1`
2. Install dependencies
   - `pip install -r requirements.txt`
3. Configure environment variables in a `.env` file
   - `GOOGLE_API_KEY=...`
   - Optional: `MODEL_NAME=gemini-flash-lite-latest`, `TEMPERATURE=0.2`, `MAX_OUTPUT_TOKENS=8192`
4. Start the backend server
   - `uvicorn app.main:app --reload --app-dir backend`

## API docs
Once the server is running, open:
- `http://127.0.0.1:8000/docs`

## Notes
- Report files such as Excel and PDF outputs may be generated during runtime and are ignored by git.
- The backend expects a valid Google AI API key to generate estimates.
