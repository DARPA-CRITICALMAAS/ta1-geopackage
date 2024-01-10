from pathlib import Path
from macrostrat.utils import working_directory
from . import create_geopackage, enable_foreign_keys
from macrostrat.database import run_sql, Database
from sqlalchemy import text
from pytest import fixture
from sqlalchemy.engine import Engine
from typing import Generator


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

    # Write the feature to the database
    # conn.execute(text(sql), dict(geom=geom))
    run_sql(
        engine,
        "INSERT INTO polygon_feature (id, map_id, map_geom) VALUES ('test', 'test', :geom)",
        params=dict(geom=feature),
        raise_errors=True,
    )

    # Read the feature back from the database
    result = run_sql(
        engine,
        "SELECT map_geom FROM polygon_feature WHERE id = 'test'",
    )
    res = result[0].fetchone()
    assert res is not None
    assert res.map_geom is not None
    assert res.map_geom == feature
