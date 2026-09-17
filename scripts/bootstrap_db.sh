#!/usr/bin/env bash
set -euo pipefail
sudo pg_ctlcluster 16 main start || true
sudo -u postgres psql -v ON_ERROR_STOP=0 -c "CREATE USER kanallar WITH PASSWORD 'kanallar' SUPERUSER;" || true
sudo -u postgres psql -v ON_ERROR_STOP=0 -c "CREATE DATABASE kanallar OWNER kanallar;" || true
PGPASSWORD=kanallar psql -h 127.0.0.1 -U kanallar -d kanallar -f "$(dirname "$0")/../database/schema.sql"
echo "PostgreSQL ready: postgresql+psycopg://kanallar:kanallar@127.0.0.1:5432/kanallar"
