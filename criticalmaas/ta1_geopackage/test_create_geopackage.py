from pathlib import Path
from macrostrat.utils import working_directory
from . import create_geopackage, enable_foreign_keys
from macrostrat.database import run_sql, Database
from pytest import fixture
from typing import Generator
import numpy as N
import fiona


@fixture(scope="function")
def empty_geopackage(tmp_path: Path) -> Generator[Path, None, None]:
    with working_directory(str(tmp_path)):
        create_geopackage("test.gpkg")
        yield tmp_path / "test.gpkg"


def tests_geopackage_file_creation(empty_geopackage: Path):
    """Create temporary geopackage file and check that it exists."""
    assert empty_geopackage.exists()


def test_write_polygon_feature_to_geopackage(empty_geopackage: Path):
    """
    Write polygon data directly to a GeoPackage file
    """
    feature = "POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))"

    # Encode the feature to a GeoPackage geometry
    from shapely import wkb, wkt
    from shapely.geometry import shape
    from shapely.geometry.base import BaseGeometry

    # Recreate the database engine
    db = Database("sqlite:///" + str(empty_geopackage))
    enable_foreign_keys(db.engine)
    engine = db.engine

    # Need to create a map and a polygon type before we do anything,
    # to make sure that foreign keys align
    run_sql(
        engine,
        """
        INSERT INTO map (id, name, source_url, image_url, image_width, image_height)
        VALUES ('test', 'test', 'test', 'test', -1, -1);

        INSERT INTO polygon_type (id, name, color)
        VALUES ('test', 'geologic unit', 'test');
        """,
        raise_errors=True,
    )

    # Read and write features

    coords = [[[(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]]]

    with fiona.open(
        str(empty_geopackage), "a", driver="GPKG", layer="polygon_feature", schema=None
    ) as src:
        feat = {
            "properties": {"id": "test", "map_id": "test"},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": coords,
            },
        }
        src.write(feat)

    with fiona.open(str(empty_geopackage), layer="polygon_feature") as src:
        assert len(src) == 1

        # To successfully read fields, you need to ignore the px_geom field,
        # which is technically not compatible with the GeoPackage spec
        # src.ignore_fields = ["px_geom"]
        feat = next(iter(src))

        assert feat["properties"]["id"] == "test"
        assert feat["properties"]["map_id"] == "test"

        assert feat["geometry"]["type"] == "MultiPolygon"
        assert N.allclose(
            feat["geometry"]["coordinates"],
            coords,
        )
