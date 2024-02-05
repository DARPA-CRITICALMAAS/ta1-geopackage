from geopandas import GeoDataFrame
from pandas import DataFrame
from pytest import mark
from shapely.geometry import MultiPolygon

from .core import GeopackageDatabase

test_map_data = {
    "id": "test",
    "name": "test",
    "source_url": "test",
    "image_url": "test",
    "image_width": 5000,
    "image_height": 5000,
}


@mark.parametrize("engine", ["fiona", "pyogrio"])
def test_write_pandas_lowlevel(empty_gpkg: GeopackageDatabase, engine: str):
    """Pandas provides a quicker way to write records to a GeoPackage.
    To use this, it is recommended to create all records and write them all at once.
    """
    gpkg = empty_gpkg

    map_df = DataFrame([test_map_data])
    map_df.to_sql("map", gpkg.engine, if_exists="append", index=False)

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
            "geometry": MultiPolygon([[[(0.0, 0.0), (0.0, i), (i, i), (i, 0.0)]]]),
        }
        for i in range(100)
    ]

    df = DataFrame(polygon_recs)
    gdf = GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(
        gpkg.file,
        layer="polygon_feature",
        driver="GPKG",
        mode="a",
        engine=engine,
        promote_to_multi=True,
    )


nonconforming_polygon = {
    "id": "zoomer",
    "type": "dishware",
    "map_id": "squiggle",
    "confidence": None,
    "provenance": None,
    "geometry": MultiPolygon([[[(0.0, 0.0), (0.0, 2), (2, 2), (2, 0.0)]]]),
}


@mark.parametrize("engine", ["fiona", "pyogrio"])
def test_write_nonconforming_data(gpkg: GeopackageDatabase, engine: str):
    """This test is to demonstrate that the GeoPackageDatabase will raise an error
    if the data does not conform to the schema.
    """

    df = DataFrame([nonconforming_polygon])
    gdf = GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(
        gpkg.file,
        driver="GPKG",
        mode="a",
        layer="polygon_feature",
        engine=engine,
        promote_to_multi=True,
    )

    # Load dataframe
    gdf_res = GeoDataFrame.from_file(gpkg.file, layer="polygon_feature")

    assert len(gdf_res) == 1
    assert gdf_res.iloc[0]["id"] == "zoomer"

    # Manually check foreign key constraints, finding failures
    with gpkg.engine.connect() as conn:
        result = conn.exec_driver_sql("PRAGMA foreign_key_check(polygon_feature)")
        assert len(result.fetchall()) == 2


def test_get_dataframe(gpkg):
    """Test getting a dataframe with GeoPandas"""
    df = gpkg.get_dataframe("map")
    assert not isinstance(df, GeoDataFrame)
    assert len(df) == 1
    assert df.iloc[0]["id"] == "test"


def test_write_pandas_basic(empty_gpkg: GeopackageDatabase):
    """Pandas provides a quicker way to write records to a GeoPackage.
    To use this, it is recommended to create all records and write them all at once.
    """
    map_df = DataFrame([test_map_data])
    empty_gpkg.write_dataframe(map_df, "map")


@mark.parametrize("engine", ["fiona", "pyogrio"])
def test_write_nonconforming_data2(gpkg: GeopackageDatabase, engine: str):
    """This test is to demonstrate that the GeoPackageDatabase will raise an error
    if the data does not conform to the schema.
    """
    df = DataFrame([nonconforming_polygon])
    gdf = GeoDataFrame(df, crs="EPSG:4326")

    try:
        gpkg.write_dataframe(gdf, "polygon_feature")
        assert False
    except ValueError as exc:
        # Not sure why we can't check the specific error type
        assert exc.table == "polygon_feature"
        assert len(exc.errors) == 2

    # Load dataframe
    gdf_res = gpkg.get_dataframe("polygon_feature")

    assert len(gdf_res) == 1
    assert gdf_res.iloc[0]["id"] == "zoomer"
