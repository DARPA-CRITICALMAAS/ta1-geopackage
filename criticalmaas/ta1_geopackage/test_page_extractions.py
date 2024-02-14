from datetime import datetime

import numpy as N
from fiona.crs import CRS
from geopandas import GeoDataFrame
from macrostrat.utils import get_logger
from shapely.geometry import MultiPolygon

from .core import GeopackageDatabase

log = get_logger(__name__)


def test_write_page_extraction(gpkg: GeopackageDatabase):
    """
    Write page extraction data directly to a GeoPackage file
    """
    db = gpkg

    db.write_models(
        [
            # map
            db.model.map(
                id="map_id123",
                name="map_id123",
                source_url="",
                image_url="",
                image_width=100,
                image_height=100,
            ),
            # model run
            db.model.model_run(
                id="model_run_id123",
                model_name="test",
                version="test",
                timestamp=str(datetime.now()),
                map_id="map_id123",
            ),
        ]
    )

    db.write_models(
        [
            # extraction identifier
            db.model.extraction_pointer(
                id="extraction_id123",
                table_name="map_metadata",
                column_name="test",
                record_id="extraction_id123",
            )
        ]
    )

    geom = MultiPolygon([[[(0.0, 0.0), (0.0, 1), (1, 1), (1, 0.0)]]])

    record = dict(
        id="page_extraction123",
        name="my_extraction",
        pointer="extraction_id123",
        model_run="model_run_id123",
        ocr_text=None,
        color_estimation=None,
        px_geometry=geom,
        bounds=None,
        confidence=None,
        provenance="modelled",
    )

    df = GeoDataFrame([record], geometry="px_geometry")

    db.write_dataframe(df, "page_extraction")
