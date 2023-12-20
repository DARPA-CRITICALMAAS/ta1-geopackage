# Resources

- [GeoPackage](https://www.geopackage.org/)
- [OGC GeoPackage spec](https://www.geopackage.org/spec120/)
- [Switch from Shapefile](http://switchfromshapefile.org/)

# Differences from TA1 schema

- `extraction_identifier` -> `extraction_pointer`
- `model` field has been renamed to `pointer` for clarity for linking models
- `MapFeatureExtractions` is replaced by many-to-one foreign key relationships
