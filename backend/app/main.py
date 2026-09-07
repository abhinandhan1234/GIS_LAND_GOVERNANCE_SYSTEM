from pathlib import Path
import os
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from psycopg2.extras import RealDictCursor

from .database import get_connection

app = FastAPI(title="Haliyal Smart Land Records API", version="1.0.0")
FRONTEND = Path(os.getenv("FRONTEND_DIR", str(Path(__file__).resolve().parents[2] / "frontend")))
LAND_TYPES = ("Agricultural", "Commercial", "Residential", "Government")
TAX_STATUSES = ("Paid", "Pending", "Overdue")
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


def feature_from_row(row):
    return {
        "type": "Feature",
        "geometry": row.pop("geometry"),
        "properties": row,
    }


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/health")
def health():
    try:
        with get_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as error:
        raise HTTPException(status_code=503, detail="Database is unavailable") from error


@app.get("/api/parcels")
def list_parcels(
    land_type: str | None = Query(default=None),
    tax_status: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=2000),
):
    if land_type and land_type not in LAND_TYPES:
        raise HTTPException(status_code=400, detail="Invalid land_type")
    if tax_status and tax_status not in TAX_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid tax_status")

    clauses, parameters = [], []
    if land_type:
        clauses.append("land_type = %s")
        parameters.append(land_type)
    if tax_status:
        clauses.append("tax_status = %s")
        parameters.append(tax_status)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    parameters.append(limit)

    query = f"""
        SELECT id, survey_number, hissa_number, owner_name, land_type,
               tax_status, village_name, ST_AsGeoJSON(geom)::json AS geometry
        FROM official_land_records
        {where}
        ORDER BY id
        LIMIT %s
    """
    with get_connection() as connection, connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, parameters)
        features = [feature_from_row(dict(row)) for row in cursor.fetchall()]
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/parcels/{parcel_id}")
def get_parcel(parcel_id: int):
    query = """
        SELECT id, survey_number, hissa_number, owner_name, land_type,
               tax_status, village_name, ST_AsGeoJSON(geom)::json AS geometry
        FROM official_land_records WHERE id = %s
    """
    with get_connection() as connection, connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, (parcel_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return feature_from_row(dict(row))


@app.get("/api/statistics")
def statistics():
    with get_connection() as connection, connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT land_type AS category, COUNT(*) AS count FROM official_land_records GROUP BY land_type ORDER BY land_type")
        by_land_type = cursor.fetchall()
        cursor.execute("SELECT tax_status AS category, COUNT(*) AS count FROM official_land_records GROUP BY tax_status ORDER BY tax_status")
        by_tax_status = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) AS count FROM official_land_records")
        total = cursor.fetchone()["count"]
    return {"total_parcels": total, "by_land_type": by_land_type, "by_tax_status": by_tax_status}
