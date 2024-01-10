UPDATE gpkg_geometry_columns
SET srs_id = :srs_id
WHERE table_name IN (
  'polygon_feature',
  'line_feature',
  'point_feature',
  'cross_section',
  'ground_control_point',
  'georeference_meta'
);