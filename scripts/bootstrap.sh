#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
cp -n frontend/.env.example frontend/.env.local || true
cp -n backend/.env.example backend/.env || true

echo "Bootstrap complete. Configure env files as needed."
