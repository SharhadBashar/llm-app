# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands
- Start dev server: `uvicorn main:app --reload`
- Start prod server: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Docker: `docker build -t fora-ai-v2 .` and `docker run -p 8000:8000 fora-ai-v2`

## Code Style Guidelines
- **Imports**: Standard lib first, then third-party, then local. Use absolute imports.
- **Types**: Use type annotations consistently. Use Pydantic models for API requests/responses.
- **Naming**: snake_case for files/variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Error handling**: Use try/except with specific error messages. Raise HTTPException with appropriate status codes.
- **Async**: Use async/await patterns with FastAPI endpoints and LLM client calls.
- **Structure**: Follow existing module organization (api/, core/, llm/, models/, services/, utils/).

## Linting & Testing
- No formal linting or testing setup exists yet
- When adding tests, use pytest
- Consider adding Black for formatting and Flake8 for linting