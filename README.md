# Resources

- [GeoPackage](https://www.geopackage.org/)
- [OGC GeoPackage spec](https://www.geopackage.org/spec120/)
- [Switch from Shapefile](http://switchfromshapefile.org/)

# Prior art

- [Fudgeo](https://github.com/realiii/fudgeo): modern Python package for working with GeoPackages. Duplicates many features of more common
  packages like `fiona` and `geopandas` but provides low-level access to the GeoPackage spec.
- [GeoPackage Python](

# Differences from TA1 schema

- `extraction_identifier` -> `extraction_pointer`
- `model` field has been renamed to `pointer` for clarity for linking models
- `MapFeatureExtractions` is replaced by many-to-one foreign key relationships
