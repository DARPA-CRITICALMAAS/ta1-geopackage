INSERT INTO gpkg_spatial_ref_sys (
  srs_name,
  srs_id,
  organization,
  organization_coordsys_id,
  definition,
  description
) VALUES (
  :srs_name,
  :srs_id,
  :organization,
  :organization_coordsys_id,
  :definition,
  :description
)
ON CONFLICT DO NOTHING;

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