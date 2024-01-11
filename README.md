# TA1 GeoPackage format

This is a starting point for a GeoPackage format for CriticalMAAS TA1. It is based on the
[TA1 output schemas](https://github.com/DARPA-CRITICALMAAS/schemas/tree/main/ta10).
The initial version was created on 2023-12-14 by Daven Quinn (Macrostrat).
It will be maintained jointly by TA1 and TA4 as the schema is updated.

![Schema diagram](diagram/schema-diagram.png)

## Installation

This Package can be installed directly from GitHub:

```bash
# PIP installation
pip install git+https://github.com/DARPA-CRITICALMAAS/ta1-geopackage.git
# Poetry
poetry add git+https://github.com/DARPA-CRITICALMAAS/ta1-geopackage.git
# etc. for other package managers
```
If you are not using Python, you can load the schema directly from
the [`criticalmaas/ta1_geopackage/fixtures`](criticalmaas/ta1_geopackage/fixtures) directory,
and use other tools such as `ogr2ogr` to load data into the database.

## Examples

Example maps (output from [Macrostrat's CLI writer](https://github.com/UW-Macrostrat/macrostrat/blob/main/macrostrat-cli/macrostrat_cli/io/criticalmaas/__init__.py)):

- [`bc_kananaskis.gpkg`](https://storage.macrostrat.org/web-assets/criticalmaas/example-files/ta1-geopackage/bc_kananaskis.gpkg): [Kananaskis Lakes, BC/AB](https://v2.macrostrat.org/maps/234), 1.5 MB
- [`grandcanyon.gpkg`](https://storage.macrostrat.org/web-assets/criticalmaas/example-files/ta1-geopackage/grandcanyon.gpkg): [Grand Canyon, AZ](https://v2.macrostrat.org/maps/34), 11.7 MB

## Usage

```python

from criticalmaas.ta1_geopackage import GeopackageDatabase

db = GeopackageDatabase("my_map.gpkg", crs="EPSG:4326")
# Can also use "CRITICALMAAS:pixel" for pixel coordinates

# Insert types (required for foreign key constraints)
db.write_models([
  db.model.map(id="test", name="test", description="test"),
  db.model.polygon_type(id="test", name="test", description="test"),
])

# Read and write features
feat ={
    "properties": {
        "id": "test",
        "map_id": "test",
        "type": "test",
        "confidence": None,
        "provenance": None,
    },
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [[[(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]]],
    },
}
db.write_features("polygon_feature", [feat])
```



## Ongoing work

- [x] Tests with geographic data
- [x] Helpers for working with multiple projections
- [ ] Example datasets
- [ ] Example script for dumping a Macrostrat map
- [ ] Schema adjustments and improvements.
- [ ] Make the package available as `criticalmass.ta1_geopackage` on PyPI.

## Resources

- [GeoPackage](https://www.geopackage.org/)
- [OGC GeoPackage spec](https://www.geopackage.org/spec120/)
- [Switch from Shapefile](http://switchfromshapefile.org/)

## Prior art

- [Fudgeo](https://github.com/realiii/fudgeo): modern Python package for working with GeoPackages. Duplicates many features of more common
  packages like `fiona` and `geopandas` but provides low-level access to the GeoPackage spec.
- [Fiona](https://fiona.readthedocs.io/en/stable/): A python library for working with geospatial vector data.
- [GeoPandas](https://geopandas.org/): A python library for working with geospatial vector data.
- [GeoAlchemy 2](https://geoalchemy-2.readthedocs.io/en/latest/): A python library for interfacing in PostGIS, Spatialite, and GeoPackage.

## Differences from TA1 schema

Several changes have been made to the TA1 schema to make it more compatible with the GeoPackage structure. See [the tracking issue](https://github.com/DARPA-CRITICALMAAS/ta1-geopackage/issues/3) for more information.
