import sqlite3
from pathlib import Path

from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely.geometry import Polygon

from . import GeopackageDatabase


def test_write_pandas(gpkg: GeopackageDatabase):
    """Pandas provides a quicker way to write records to a GeoPackage.
    To use this, it is recommended to create all records and write them all at once.
    """

    # Records to be written
    dtype = {
        "id": "test",
        "name": "geologic unit",
        "color": "test",
    }

    types = DataFrame([dtype])

    types.to_sql("polygon_type", gpkg.engine, if_exists="append", index=False)

    polygon_recs = [
        {
            "id": f"test.{i}",
            "map_id": "test",
            "type": "test",
            "confidence": None,
            "provenance": None,
            "geometry": Polygon([(0.0, 0.0), (0.0, i), (i, i), (i, 0.0)]),
        }
        for i in range(100)
    ]

    df = DataFrame(polygon_recs)
    gdf = GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(gpkg.file, layer="polygon_feature", driver="GPKG", append=True)


def test_write_nonconforming_data(gpkg: GeopackageDatabase):
    """This test is to demonstrate that the GeoPackageDatabase will raise an error
    if the data does not conform to the schema.
    """
    polygon_rec = {
        "id": "testzzz",
        "type": "test",
        "confidence": None,
        "provenance": None,
        "geometry": Polygon([(0.0, 0.0), (0.0, 2), (2, 2), (2, 0.0)]),
    }

    df = DataFrame([polygon_rec])
    gdf = GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(gpkg.file, layer="polygon_feature", driver="GPKG", append=True)

    # Copy file to accessible location
    import shutil

    here = Path(__file__).parent

    shutil.copy(gpkg.file, here / "test.gpkg")

    # Manually check foreign key constraints
    with gpkg.engine.connect() as conn:
        result = conn.exec_driver_sql("PRAGMA foreign_key_check(polygon_feature)")
        assert len(result.fetchall()) > 0
