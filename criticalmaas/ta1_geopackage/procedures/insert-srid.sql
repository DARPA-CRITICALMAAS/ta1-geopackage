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

