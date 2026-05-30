# Repository Structure

This repository uses production-style folder naming to make ownership and deployment boundaries explicit.

- `frontend/`: user-facing web interface assets and UI contracts.
- `backend/`: API endpoints, service logic, schemas, and backend tests.
- `workers/`: asynchronous processors and queue consumers.
- `infrastructure/`: deployment resources and IaC modules.
- `monitoring/`: observability configuration and dashboard provisioning.
- `scripts/`: repeatable local and CI helper commands.
- `tests/`: cross-service tests that validate platform behavior.
