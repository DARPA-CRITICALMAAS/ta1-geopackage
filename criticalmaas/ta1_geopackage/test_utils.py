from . import GeopackageDatabase


def _write_test_types(gpkg: GeopackageDatabase):
    gpkg.run_sql(
        """
        INSERT INTO map (id, name, source_url, image_url, image_width, image_height)
        VALUES ('test', 'test', 'test', 'test', -1, -1);

        INSERT INTO polygon_type (id, name, color)
        VALUES ('test', 'geologic unit', 'test');
        """,
        raise_errors=True,
    )
