from . import GeopackageDatabase


def test_write_pandas(gpkg: GeopackageDatabase):
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Polygon

    types = pd.DataFrame(
        {
            "id": ["test"],
            "name": ["geologic unit"],
            "color": ["test"],
        }
    )

    types.to_sql("polygon_type", gpkg.engine, if_exists="replace", index=False)

    df = pd.DataFrame(
        {
            "id": ["test"],
            "map_id": ["test"],
            "type": ["test"],
            "confidence": [None],
            "provenance": [None],
            "geometry": [Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)])],
        }
    )
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")

    gdf.to_file(gpkg.file, layer="polygon_feature", driver="GPKG")
