from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely.geometry import MultiPolygon

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
        promote_to_multi=True,
    )


def test_write_nonconforming_data(gpkg: GeopackageDatabase):
    """This test is to demonstrate that the GeoPackageDatabase will raise an error
    if the data does not conform to the schema.
    """
    polygon_rec = {
        "id": "zoomer",
        "type": "dishware",
        "map_id": "squiggle",
        "confidence": None,
        "provenance": None,
        "geometry": MultiPolygon([[[(0.0, 0.0), (0.0, 2), (2, 2), (2, 0.0)]]]),
    }

    df = DataFrame([polygon_rec])
    gdf = GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(
        gpkg.file,
        driver="GPKG",
        mode="a",
        layer="polygon_feature",
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
