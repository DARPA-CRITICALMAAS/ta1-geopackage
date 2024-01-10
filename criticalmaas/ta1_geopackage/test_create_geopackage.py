from pathlib import Path
from macrostrat.utils import working_directory
from . import GeopackageDatabase
from macrostrat.database import run_sql
from pytest import fixture
from typing import Generator
import numpy as N
import fiona


@fixture(scope="function")
def empty_geopackage(tmp_path: Path) -> Generator[GeopackageDatabase, None, None]:
    with working_directory(str(tmp_path)):
        db = GeopackageDatabase(tmp_path / "test.gpkg")
        db.create_fixtures()
        yield db


def tests_geopackage_file_creation(empty_geopackage: GeopackageDatabase):
    """Create temporary geopackage file and check that it exists."""
    assert empty_geopackage.file.exists()


def test_write_polygon_feature_to_geopackage(empty_geopackage: GeopackageDatabase):
    """
    Write polygon data directly to a GeoPackage file
    """

    # Need to create a map and a polygon type before we do anything,
    # to make sure that foreign keys align
    empty_geopackage.run_sql(
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
            "coordinates": coords,
        },
    }
    empty_geopackage.write_features("polygon_feature", [feat])

    with empty_geopackage.open_layer("polygon_feature") as src:
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
