/** GeoPackage / SQLite schema for DARPA CriticalMAAS TA1 data output.
*   
*   Based on TA1 output schemas:
*   https://github.com/DARPA-CRITICALMAAS/schemas/tree/main/ta1
*
*   Initial version created on 2023-12-14 by Daven Quinn (Macrostrat)
*/

CREATE TABLE map (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  name TEXT NOT NULL, -- name of the map
  source_url TEXT NOT NULL, -- URL of the map source (e.g., NGMDB information page)
  image_url TEXT NOT NULL, -- URL of the map image, as a web-accessible, cloud-optimized GeoTIFF
  image_width INTEGER NOT NULL, -- width of the map image, in pixels
  image_height INTEGER NOT NULL -- height of the map image, in pixels
);

CREATE TABLE geologic_unit (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  name TEXT, -- name of the geologic unit
  description TEXT, -- description of the geologic unit
  age_text TEXT, -- age of the geologic unit, textual description
  t_interval TEXT, -- geologic time interval, youngest
  b_interval TEXT, -- geologic time interval, oldest
  t_age REAL, -- Minimum age (Ma)
  b_age REAL, -- Maximum age (Ma)
  lithology TEXT -- comma-separated array of lithology descriptors extracted from legend text
);

CREATE TABLE polygon_type (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  name TEXT NOT NULL, -- name of the polygon type
  color TEXT NOT NULL , -- color extracted from map/legend
  pattern TEXT, -- pattern extracted from map/legend
  abbreviation TEXT, -- abbreviation extracted from map/legend
  description TEXT, -- description text extracted from legend
  category TEXT, -- name of containing legend block
  map_unit TEXT, -- map unit information
  FOREIGN KEY (map_unit) REFERENCES geologic_unit(id),
  FOREIGN KEY (name) REFERENCES enum_polygon_type(name)
);

CREATE TABLE line_type (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  name TEXT NOT NULL, -- name of the line type
  description TEXT, -- description of the line type
  dash_pattern TEXT, -- dash pattern extracted from map/legend
  symbol TEXT, -- symbol extracted from map/legend
  FOREIGN KEY (name) REFERENCES enum_line_type(name)
);


CREATE TABLE polygon_feature (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  map_geom POLYGON NOT NULL, -- polygon geometry, world coordinates
  px_geom POLYGON, -- polygon geometry, pixel coordinates
  type TEXT, -- polygon type information
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (type) REFERENCES polygon_type(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

CREATE TABLE line_feature (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  map_geom LINESTRING NOT NULL, -- line geometry, world coordinates
  px_geom LINESTRING, -- line geometry, pixel coordinates
  name TEXT, -- name of this map feature
  type TEXT, -- line type information
  polarity INTEGER, -- line polarity
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (type) REFERENCES line_type(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name),
  FOREIGN KEY (polarity) REFERENCES enum_line_polarity(value)
);


CREATE TABLE point_type (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  name TEXT NOT NULL, -- name of the point type
  description TEXT, -- description of the point type
  FOREIGN KEY (name) REFERENCES enum_point_type(name)
);

CREATE TABLE point_feature (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  map_geom POINT NOT NULL, -- point geometry, world coordinates
  px_geom POINT, -- point geometry, pixel coordinates
  type TEXT, -- point type information
  dip_direction REAL, -- dip direction
  dip REAL, -- dip
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (type) REFERENCES point_type(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

/** Note: renamed `extraction_identifier` to `extraction_pointer` for clarity */
CREATE TABLE extraction_pointer (
  id TEXT PRIMARY KEY,
  table_name TEXT NOT NULL, -- model name
  column_name TEXT NOT NULL, -- field name of the model
  record_id TEXT NOT NULL, -- ID of the extracted feature
  FOREIGN KEY (table_name) REFERENCES enum_table_name(name)
);

CREATE TABLE confidence_scale (
  name TEXT PRIMARY KEY, -- name of the confidence scale
  description TEXT NOT NULL, -- description of the confidence scale
  min_value REAL NOT NULL, -- minimum value
  max_value REAL NOT NULL -- maximum value
);

CREATE TABLE model_run (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  model_name TEXT NOT NULL, -- model name
  version TEXT NOT NULL, -- model version
  timestamp TEXT NOT NULL, -- time of model run
  batch_id TEXT -- batch ID
);

CREATE TABLE map_model_run (
  map_id TEXT NOT NULL, -- ID of the containing map
  model_run TEXT NOT NULL, -- model run ID
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (model_run) REFERENCES model_run(id),
  PRIMARY KEY (map_id, model_run)
);

CREATE TABLE confidence_measurement (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  model_run TEXT NOT NULL, -- model run ID
  pointer TEXT NOT NULL, -- model name
  confidence REAL NOT NULL, -- confidence value
  scale TEXT NOT NULL, -- confidence scale
  extra_data TEXT, -- additional data (JSON)
  FOREIGN KEY (pointer) REFERENCES extraction_pointer(id),
  FOREIGN KEY (scale) REFERENCES confidence_scale(name)
);


CREATE TABLE page_extraction (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  name TEXT NOT NULL, -- name of the page extraction object
  pointer TEXT NOT NULL, -- pointer to the extraction
  model_run TEXT NOT NULL, -- model run ID
  ocr_text TEXT, -- OCR text of the page extraction
  color_estimation TEXT, -- color estimation
  bounds TEXT NOT NULL, -- bounds of the page extraction, in pixel coordinates
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (pointer) REFERENCES extraction_pointer(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);


CREATE TABLE ground_control_point (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  map_geom POINT NOT NULL, -- point geometry, world coordinates
  px_geom POINT, -- point geometry, pixel coordinates
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

CREATE TABLE cross_section (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  line_of_section LINESTRING NOT NULL, -- line geometry, world coordinates
  px_geom LINESTRING, -- line geometry, pixel coordinates
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

CREATE TABLE geo_reference_meta (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  projection TEXT NOT NULL, -- Map projection information
  bounds POLYGON NOT NULL, -- Polygon boundary of the map area, in world coordinates
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

CREATE TABLE map_metadata (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  authors TEXT NOT NULL, -- Map authors
  publisher TEXT NOT NULL, -- Map publisher
  year INTEGER NOT NULL, -- Map publication year
  organization TEXT NOT NULL, -- Map organization
  scale TEXT NOT NULL, -- Map scale
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

INSERT INTO gpkg_spatial_ref_sys (
  srs_name, srs_id, organization, organization_coordsys_id, definition, description)
  VALUES
  ('WGS 84', 4326, 'EPSG', 4326, 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]', 'WGS 84'),
  ('Pixel coordinates', 0, 'CRITICALMAAS', 0, 'PIXELCS["Pixel coordinates", ENGRUNITS["m", 1.0]]', 'Pixel coordinates');

INSERT INTO gpkg_contents (table_name, data_type, identifier, description)
  VALUES
  ('polygon_feature', 'features', 'polygon_feature', 'Polygon map features'),
  ('line_feature', 'features', 'line_feature', 'Line map features'),
  ('point_feature', 'features', 'point_feature', 'Point map features'),
  ('cross_section', 'features', 'cross_section', 'Lines of section'),
  ('projection_info', 'features', 'projection_info', 'Map projection information'),
  ('ground_control_point', 'features', 'ground_control_point', 'Ground control point'),
  ('page_extraction', 'features', 'page_extraction', 'Page extractions');

INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m)
  VALUES
  ('polygon_feature', 'map_geom', 'POLYGON', 4326, 0, 0),
  ('line_feature', 'map_geom', 'LINESTRING', 4326, 0, 0),
  ('point_feature', 'map_geom', 'POINT', 4326, 0, 0),
  ('cross_section', 'line_of_section', 'LINESTRING', 4326, 0, 0),
  ('ground_control_point', 'map_geom', 'POINT', 4326, 0, 0),
  ('page_extraction', 'bounds', 'POLYGON', 0, 0, 0);
  -- ('polygon_feature', 'px_geom', 'POLYGON', 0, 0, 0),
  -- ('line_feature', 'px_geom', 'LINESTRING', 0, 0, 0),
  -- ('point_feature', 'px_geom', 'POINT', 0, 0, 0),
  -- ('cross_section', 'px_geom', 'LINESTRING', 0, 0, 0),
  -- ('ground_control_point', 'px_geom', 'POINT', 0, 0, 0);

-- Create an empty geometry_columns table so that Geoalchemy2 doesn't complain
CREATE TABLE geometry_columns (
  f_table_name TEXT NOT NULL,
  f_geometry_column TEXT NOT NULL,
  geometry_type INTEGER NOT NULL,
  coord_dimension INTEGER NOT NULL,
  srid INTEGER NOT NULL,
  geometry_format TEXT NOT NULL
);