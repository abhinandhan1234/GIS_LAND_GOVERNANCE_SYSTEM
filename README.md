# Haliyal Smart Land Records Prototype

A local GIS prototype for visualising and querying synthetic cadastral land parcels around Haliyal, Karnataka. It uses PostgreSQL/PostGIS for spatial storage, FastAPI for a GeoJSON REST API, and Leaflet for an interactive map.

## Features

- Generates 500 unique synthetic survey and hissa records using Indian-localised Faker names.
- Stores SRID 4326 cadastral polygons and land attributes in PostGIS.
- Exposes GeoJSON parcel data, individual parcel lookup, filtering, and summary statistics.
- Provides an interactive map with parcel popups, land-type filters, tax-status filters, and an inspector panel.
- Boots the database schema automatically through Docker Compose.

## Quick start

1. Install Docker Desktop and start it.
2. Copy `.env.example` to `.env` if you need different database credentials.
3. Run `docker compose up --build -d`.
4. Install Python dependencies locally: `pip install -r backend/requirements.txt`.
5. Seed the database: `python scripts/generate_land_records.py`.
6. Open `http://localhost:8000`.

## API endpoints

- `GET /health` checks database connectivity.
- `GET /api/parcels` returns filtered parcel GeoJSON. Optional: `land_type`, `tax_status`, `limit`.
- `GET /api/parcels/{parcel_id}` returns one parcel as GeoJSON.
- `GET /api/statistics` returns counts by land type and tax status.

## Local development without Docker API

Start only the database with `docker compose up -d postgis`, then run:

```powershell
$env:DATABASE_URL = "postgresql://postgres:password@localhost:5432/land_records"
uvicorn app.main:app --app-dir backend --reload
```

