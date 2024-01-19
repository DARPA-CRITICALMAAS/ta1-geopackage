# CriticalMAAS TA1 geopackage library

This repository contains schema definitions and
a reference Python library for manipulating a GeoPackage-based data transfer format for CriticalMAAS TA1, based on
the [TA1 output
schemas][ta1_schemas].  It was
created by the [Macrostrat TA4
team](https://github.com/UW-Macrostrat/criticalmaas) and will be maintained
jointly by TA1 and TA4 as the schema is updated.

## Installation

This package is listed as `criticalmaas.ta1-geopackage` on [PyPI][pypi].
It can be installed with standard Python semantics:

```bash
# PIP installation
pip install criticalmaas.ta1-geopackage
# Poetry
poetry add criticalmaas.ta1-geopackage
```

The package can also be installed directly from GitHub, e.g. `pip install git+https://github.com/DARPA-CRITICALMAAS/ta1-geopackage.git`.

If you are not using Python, you can load the schema directly from
the [`criticalmaas/ta1_geopackage/fixtures`](criticalmaas/ta1_geopackage/fixtures) directory,
and use other tools such as `ogr2ogr` to load data into the database.

## Examples

Example maps (output from [Macrostrat's CLI writer][macrostrat_writer]):

- [`bc_kananaskis.gpkg`](https://storage.macrostrat.org/web-assets/criticalmaas/example-files/ta1-geopackage/bc_kananaskis.gpkg): [Kananaskis Lakes, BC/AB](https://v2.macrostrat.org/maps/234), 1.5 MB
- [`grandcanyon.gpkg`](https://storage.macrostrat.org/web-assets/criticalmaas/example-files/ta1-geopackage/grandcanyon.gpkg): [Grand Canyon, AZ](https://v2.macrostrat.org/maps/34), 11.7 MB

At the moment, these only show final feature datasets (e.g. `polygon_feature`) for digital-native maps. Examples of
TA1 output for raster-based maps will be added soon.

## Usage

Basic usage is as follows:

```python

from criticalmaas.ta1_geopackage import GeopackageDatabase

db = GeopackageDatabase(
  "my_map.gpkg",
  crs="EPSG:4326" # Geographic coordinates (default)
  # crs="CRITICALMAAS:pixel" # Pixel coordinates
)

# Insert types (required for foreign key constraints)
db.write_models([
  db.model.map(id="test", name="test", description="test"),
  db.model.polygon_type(id="test", name="test", description="test"),
])

# Write features
feat = {
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

See the [tests][tests] and the [Macrostrat CLI writer][macrostrat_writer] for more examples.

## Schema

![Schema diagram](diagram/schema-diagram.png)

## Ongoing work

- [x] Tests with geographic data
- [x] Helpers for working with multiple projections
- [x] Example datasets
- [x] Example script for dumping a Macrostrat map
- [x] Schema adjustments and improvements (see [tracking issue][change-tracking-issue])
- [x] Make the package available as `criticalmass.ta1_geopackage` on PyPI.
- [ ] Create example of writing `page_extraction`s with pixel coordinates

## Resources

- [GeoPackage](https://www.geopackage.org/)
- [OGC GeoPackage spec](https://www.geopackage.org/spec120/)
- [Switch from Shapefile](http://switchfromshapefile.org/)

## Prior art

- [Fiona](https://fiona.readthedocs.io/en/stable/): A python library for working with geospatial vector data.
- [GeoPandas](https://geopandas.org/): A python library for working with geospatial vector data.
- [GeoAlchemy 2](https://geoalchemy-2.readthedocs.io/en/latest/): A python library for interfacing in PostGIS, Spatialite, and GeoPackage.
- [Fudgeo](https://github.com/realiii/fudgeo): modern Python package for working with GeoPackages. Duplicates many features of more common
  packages like `fiona` and `geopandas` but provides low-level access to the GeoPackage spec.

[macrostrat_writer]: https://github.com/UW-Macrostrat/macrostrat/blob/main/cli/macrostrat/cli/io/criticalmaas/__init__.py
[tests]: criticalmaas/ta1_geopackage/test_create_geopackage.py
[change-tracking-issue]: https://github.com/DARPA-CRITICALMAAS/ta1-geopackage/issues/3
[pypi]: https://pypi.org/project/criticalmaas.ta1-geopackage/
[ta1_schemas]: https://github.com/DARPA-CRITICALMAAS/schemas/tree/main/ta1
