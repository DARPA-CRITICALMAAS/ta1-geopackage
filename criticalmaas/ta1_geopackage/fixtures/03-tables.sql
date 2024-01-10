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
  geometry MULTIPOLYGON NOT NULL, -- polygon geometry, world coordinates
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
  geometry MULTILINESTRING NOT NULL, -- line geometry, world coordinates
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
  geometry POINT NOT NULL, -- point geometry, world coordinates
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
  batch_id TEXT, -- batch ID
  map_id TEXT NOT NULL, -- ID of the containing map
  FOREIGN KEY (map_id) REFERENCES map(id)
);

CREATE TABLE confidence_measurement (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  model_run TEXT NOT NULL, -- model run ID
  pointer TEXT NOT NULL, -- model name
  confidence REAL NOT NULL, -- confidence value
  scale TEXT NOT NULL, -- confidence scale
  extra_data TEXT, -- additional data (JSON)
  FOREIGN KEY (model_run) REFERENCES model_run(id),
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
  px_geometry GEOMETRY, -- geometry of the page extraction, in pixel coordinates
  bounds TEXT NOT NULL, -- bounds of the page extraction, in pixel coordinates
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (pointer) REFERENCES extraction_pointer(id),
  FOREIGN KEY (model_run) REFERENCES model_run(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);


CREATE TABLE ground_control_point (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  geometry POINT NOT NULL, -- point geometry, world coordinates
  x REAL NOT NULL, -- x coordinate, pixel coordinates
  y REAL NOT NULL, -- y coordinate, pixel coordinates
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

CREATE TABLE cross_section (
  id TEXT PRIMARY KEY, -- for internal linking purposes in this file
  map_id TEXT NOT NULL, -- ID of the containing map
  geometry LINESTRING NOT NULL, -- line geometry, world coordinates
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

CREATE TABLE georeference_meta (
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
  title TEXT NOT NULL, -- Map title
  publisher TEXT NOT NULL, -- Map publisher
  year INTEGER NOT NULL, -- Map publication year
  organization TEXT, -- Map organization
  scale TEXT, -- Map scale
  confidence REAL, -- confidence associated with this extraction
  provenance TEXT, -- provenance for this extraction
  FOREIGN KEY (map_id) REFERENCES map(id),
  FOREIGN KEY (provenance) REFERENCES enum_provenance_type(name)
);

INSERT INTO gpkg_spatial_ref_sys (
  srs_name, srs_id, organization, organization_coordsys_id, definition, description)
  VALUES
  ('Pixel coordinates', 0, 'CRITICALMAAS', 0, 'PIXELCS["Pixel coordinates", ENGRUNITS["m", 1.0]]', 'Pixel coordinates');

INSERT INTO gpkg_contents (table_name, data_type, identifier, description)
  VALUES
  ('polygon_feature', 'features', 'polygon_feature', 'Polygon map features'),
  ('line_feature', 'features', 'line_feature', 'Line map features'),
  ('point_feature', 'features', 'point_feature', 'Point map features'),
  ('cross_section', 'features', 'cross_section', 'Lines of section'),
  ('projection_info', 'features', 'projection_info', 'Map projection information'),
  ('ground_control_point', 'features', 'ground_control_point', 'Ground control point'),
  ('georeference_meta', 'features', 'georeference_meta', 'Georeferencing metadata'),
  ('page_extraction', 'features', 'page_extraction', 'Page extractions');

INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m)
  VALUES
  ('polygon_feature', 'geometry', 'MULTIPOLYGON', 0, 0, 0),
  ('line_feature', 'geometry', 'MULTILINESTRING', 0, 0, 0),
  ('point_feature', 'geometry', 'POINT', 0, 0, 0),
  ('cross_section', 'geometry', 'LINESTRING', 0, 0, 0),
  ('ground_control_point', 'geometry', 'POINT', 0, 0, 0),
  ('georeference_meta', 'bounds', 'POLYGON', 0, 0, 0),
  ('page_extraction', 'px_geometry', 'GEOMETRY', 0, 0, 0);

-- Create an empty geometry_columns table so that Geoalchemy2 doesn't complain
CREATE TABLE geometry_columns (
  f_table_name TEXT NOT NULL,
  f_geometry_column TEXT NOT NULL,
  geometry_type INTEGER NOT NULL,
  coord_dimension INTEGER NOT NULL,
  srid INTEGER NOT NULL,
  geometry_format TEXT NOT NULL
);