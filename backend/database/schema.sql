-- AutoRouteAI PostgreSQL + PostGIS Schema

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Road segments ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS road_segments (
    id              BIGSERIAL PRIMARY KEY,
    way_id          BIGINT UNIQUE,          -- OSM way ID
    city            VARCHAR(64) NOT NULL,
    name            TEXT,
    highway_type    VARCHAR(64),
    surface         VARCHAR(64),
    smoothness      VARCHAR(64),
    lanes           INTEGER,
    width_m         FLOAT,
    road_score      FLOAT DEFAULT 0.5,
    driver_score    FLOAT DEFAULT 0.5,
    accident_risk   FLOAT DEFAULT 0.0,
    flood_risk      FLOAT DEFAULT 0.0,
    geom            GEOMETRY(LINESTRING, 4326),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_road_segments_city ON road_segments(city);
CREATE INDEX IF NOT EXISTS idx_road_segments_geom ON road_segments USING GIST(geom);

-- ── Driver feedback ───────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS driver_feedback (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id    VARCHAR(128),
    city        VARCHAR(64),
    rating      SMALLINT CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    sentiment   VARCHAR(16),            -- positive | negative | neutral
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── Accident data ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS accidents (
    id          BIGSERIAL PRIMARY KEY,
    city        VARCHAR(64),
    lat         FLOAT NOT NULL,
    lng         FLOAT NOT NULL,
    severity    SMALLINT DEFAULT 1,     -- 1=minor, 2=serious, 3=fatal
    occurred_at TIMESTAMPTZ,
    geom        GEOMETRY(POINT, 4326),
    way_id      BIGINT REFERENCES road_segments(way_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_accidents_geom ON accidents USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_accidents_city ON accidents(city);

-- ── Traffic observations ──────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS traffic_observations (
    id              BIGSERIAL PRIMARY KEY,
    city            VARCHAR(64),
    lat             FLOAT,
    lng             FLOAT,
    congestion      FLOAT,              -- 0–1
    hour_of_day     SMALLINT,
    day_of_week     SMALLINT,
    observed_at     TIMESTAMPTZ DEFAULT NOW(),
    geom            GEOMETRY(POINT, 4326)
);

CREATE INDEX IF NOT EXISTS idx_traffic_city_time ON traffic_observations(city, hour_of_day, day_of_week);
