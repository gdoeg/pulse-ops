# PulseOps

PulseOps is a production reliability engineering platform organized as a professional monorepo with clear ownership boundaries for applications, workers, infrastructure, and operational tooling.

## Architecture Overview

- **frontend/**: Next.js + TypeScript + Tailwind web console.
- **backend/**: FastAPI service layer and API contracts.
- **workers/**: Background job processors and async workloads.
- **infrastructure/**: Deployment, container, and IaC assets.
- **docs/**: Architecture and operational documentation.
- **monitoring/**: Observability assets (Prometheus/Grafana placeholders).
- **scripts/**: Developer and CI utility scripts.
- **tests/**: Cross-service integration and end-to-end tests.

## Repository Organization

```text
pulse-ops/
├── frontend/            # Web application (Next.js + TypeScript + Tailwind)
├── backend/             # API service (FastAPI)
├── workers/             # Async/background processing services
├── infrastructure/      # Docker/IaC/deployment resources
├── docs/                # Engineering and architecture documentation
├── monitoring/          # Dashboards, alerts, and scrape config
├── scripts/             # Local development and automation scripts
├── tests/               # Repository-level integration/e2e tests
├── docker-compose.yml   # Local service orchestration
├── Makefile             # Common development commands
└── .pre-commit-config.yaml
```

## Quick Start

1. Copy environment templates:
   - `cp .env.example .env`
   - `cp frontend/.env.example frontend/.env.local`
   - `cp backend/.env.example backend/.env`
2. Start local dependencies:
   - `docker compose up -d postgres redis`
3. Run services:
   - `make dev-frontend`
   - `make dev-backend`
   - `make dev-workers`

## Notes

This scaffold intentionally includes placeholders for production health checks, observability configs, and CI pipelines so teams can evolve each area without reorganizing the repository.
