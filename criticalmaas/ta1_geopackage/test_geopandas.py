from . import GeopackageDatabase


def test_write_pandas(gpkg: GeopackageDatabase):
    """Pandas provides a quicker way to write records to a GeoPackage.
    To use this, it is recommended to create all records and write them all at once.
    """
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Polygon

    # Records to be written
    dtype = {
        "id": "test",
        "name": "geologic unit",
        "color": "test",
    }

    types = pd.DataFrame([dtype])

    types.to_sql("polygon_type", gpkg.engine, if_exists="replace", index=False)

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

    df = pd.DataFrame(polygon_recs)

    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(gpkg.file, layer="polygon_feature", driver="GPKG")
