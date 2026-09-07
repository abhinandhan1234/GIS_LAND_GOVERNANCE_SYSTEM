CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS official_land_records (
    id SERIAL PRIMARY KEY,
    survey_number VARCHAR(20) NOT NULL,
    hissa_number VARCHAR(10) NOT NULL,
    owner_name VARCHAR(150) NOT NULL,
    land_type VARCHAR(30) NOT NULL CHECK (land_type IN ('Agricultural', 'Commercial', 'Residential', 'Government')),
    tax_status VARCHAR(20) NOT NULL CHECK (tax_status IN ('Paid', 'Pending', 'Overdue')),
    village_name VARCHAR(100) NOT NULL DEFAULT 'Haliyal',
    geom geometry(Polygon, 4326) NOT NULL,
    CONSTRAINT official_land_records_survey_hissa_key UNIQUE (survey_number, hissa_number)
);

CREATE INDEX IF NOT EXISTS official_land_records_geom_gix
    ON official_land_records USING GIST (geom);

CREATE INDEX IF NOT EXISTS official_land_records_attributes_idx
    ON official_land_records (land_type, tax_status);

