
-- psql -h localhost -p 5432 -U postgres -d pixels -a -f create_tables.sql -W

-- Create unique table for imagery index from csv's 
CREATE TABLE  IF NOT EXISTS imagery (
  ID  bigserial PRIMARY KEY, 
  SCENE_ID varchar(255),
  PRODUCT_ID varchar(255),
  SPACECRAFT_ID varchar(255),
  SENSOR_ID varchar(255),
  DATE_ACQUIRED date,
  COLLECTION_NUMBER serial,
  COLLECTION_CATEGORY varchar(255),
  SENSING_TIME timestamp,
  DATA_TYPE varchar(255),
  WRS_PATH serial,
  WRS_ROW serial,
  CLOUD_COVER numeric,
  NORTH_LAT numeric,
  SOUTH_LAT numeric,
  WEST_LON numeric,
  EAST_LON numeric,
  TOTAL_SIZE bigint,
  BASE_URL varchar(255),
  GRANULE_ID varchar(255),
  DATATAKE_IDENTIFIER varchar(255),
  MGRS_TILE varchar(255),
  GEOMETRIC_QUALITY_FLAG text,
  GENERATION_TIME timestamp,
  bbox GEOMETRY);

\COPY imagery(SCENE_ID,PRODUCT_ID,SPACECRAFT_ID,SENSOR_ID,DATE_ACQUIRED,COLLECTION_NUMBER,COLLECTION_CATEGORY,SENSING_TIME,DATA_TYPE, WRS_PATH,WRS_ROW,CLOUD_COVER,NORTH_LAT,SOUTH_LAT,WEST_LON,EAST_LON,TOTAL_SIZE,BASE_URL, bbox) FROM '/home/keren/projects/API_Images/landsat/new/index_landsat_2.csv' WITH (FORMAT CSV,HEADER true, DELIMITER ',');

\COPY imagery(GRANULE_ID, PRODUCT_ID, DATATAKE_IDENTIFIER, MGRS_TILE, SENSING_TIME, TOTAL_SIZE, CLOUD_COVER, GEOMETRIC_QUALITY_FLAG, GENERATION_TIME, NORTH_LAT, SOUTH_LAT, WEST_LON, EAST_LON, BASE_URL, bbox) FROM '/home/keren/projects/API_Images/sentinel/new/index_s2_l1c_2.csv' WITH (FORMAT CSV,HEADER true, DELIMITER ',');

\COPY imagery(GRANULE_ID, PRODUCT_ID, DATATAKE_IDENTIFIER, MGRS_TILE, SENSING_TIME, TOTAL_SIZE, CLOUD_COVER, GEOMETRIC_QUALITY_FLAG, GENERATION_TIME, NORTH_LAT, SOUTH_LAT, WEST_LON, EAST_LON, BASE_URL, bbox) FROM '/home/keren/projects/API_Images/sentinel/new/index_s2_l2a_2.csv' WITH (FORMAT CSV,HEADER true, DELIMITER ',');

-- Fill null values in spacecraft_id column with 'sentinel_2' for platform query
UPDATE imagery
SET spacecraft_id = 'SENTINEL_2'
WHERE spacecraft_id IS NULL;

-- Create indexes
CREATE INDEX coord  -- Duration ~5min
ON imagery (north_lat, south_lat,east_lon, west_lon);

-- Create multi-collumns index for full querry
CREATE INDEX queries
ON imagery (spacecraft_id, sensing_time, cloud_cover, north_lat, south_lat,east_lon, west_lon);  -- Duration ~5min

CREATE INDEX cloud_cover
ON imagery (cloud_cover);

CREATE INDEX sensing_time
ON imagery (sensing_time);

CREATE INDEX spacecraft_id
ON imagery (spacecraft_id);

CREATE INDEX product_id
ON imagery (product_id); -- ~8min

CREATE INDEX granule
ON imagery(granule_id);
-- PostGIS
CREATE EXTENSION postgis;

-- AddGeometryColumn([<schema_name>],<table_name>,<column_name>, <srid>, <type>,<dimension>);
-- SELECT AddGeometryColumn('public', 'imagery','geom', 4326, 'POLYGON',2)

--Populating geometry column
--UPDATE imagery SET geom = ST_MakeEnvelope(west_lon, south_lat, east_lon, north_lat, 4326) WHERE id=id;

-- Update bbox colum to SRID 4326
SELECT UpdateGeometrySRID('imagery','bbox',4326);

-- Create index to speed up spatial query
CREATE INDEX geo
ON imagery USING GIST (bbox); -- Duration ~15min


