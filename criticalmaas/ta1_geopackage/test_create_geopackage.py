import numpy as N
from fiona.crs import CRS
from macrostrat.utils import get_logger
from sqlalchemy.exc import IntegrityError

from .core import GeopackageDatabase

log = get_logger(__name__)


def tests_geopackage_file_creation(empty_gpkg: GeopackageDatabase):
    """Create temporary geopackage file and check that it exists."""
    assert empty_gpkg.file.exists()


def test_write_polygon_feature_to_geopackage(gpkg: GeopackageDatabase):
    """
    Write polygon data directly to a GeoPackage file
    """

    # Need to create a map and a polygon type before we do anything,
    # to make sure that foreign keys align
    # Read and write features
    _write_test_features(gpkg)


def test_failing_enum_constraint(empty_gpkg: GeopackageDatabase):
    gpkg = empty_gpkg
    PolygonType = gpkg.model.polygon_type

    models = [
        PolygonType(id="test", name="nonexistent-type", color="test"),
    ]
    try:
        gpkg.write_models(models)
        assert False
    except IntegrityError as exc:
        assert "FOREIGN KEY constraint failed" in str(exc)


def test_write_polygon_feature_automapped(empty_gpkg: GeopackageDatabase):
    gpkg = empty_gpkg
    Map = gpkg.model.map
    PolygonType = gpkg.model.polygon_type

    models = [
        Map(
            id="test",
            name="test",
            source_url="test",
            image_url="test",
            image_width=5000,
            image_height=5000,
        ),
        PolygonType(id="test", name="geologic unit", color="test"),
    ]
    gpkg.write_models(models)

    _write_test_features(gpkg)


def _write_test_features(gpkg: GeopackageDatabase):
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
    gpkg.write_features("polygon_feature", [feat])

    with gpkg.open_layer("polygon_feature") as src:
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


def test_geographic_proj():
    proj = CRS.from_string("EPSG:4326")
    assert proj.is_geographic


def test_non_geographic_proj():
    proj = CRS.from_string("EPSG:32612")
    assert not proj.is_geographic
    assert proj.to_epsg() == 32612


def test_proj_user_input():
    proj = CRS.from_user_input(32612)
    assert not proj.is_geographic
    assert proj.to_epsg() == 32612

    proj1 = CRS.from_user_input(proj)
    assert proj1 == proj


def get_proj_srs_id(proj: CRS):
    return proj.to_epsg()


def test_geopackage_wgs84(gpkg: GeopackageDatabase):
    val = next(
        gpkg.run_sql(
            "SELECT srs_id FROM gpkg_geometry_columns WHERE table_name = :table_name",
            params={"table_name": "polygon_feature"},
        )
    ).scalar()

    assert val == 4326

    with gpkg.open_layer("polygon_feature") as src:
        assert src.crs.is_geographic
        assert src.crs.to_epsg() == 4326


def test_create_geopackage_alt_projection(gpkg: GeopackageDatabase):
    """
    Create a GeoPackage with an alternate projection
    """
    crs_string = "EPSG:32612"
    proj = CRS.from_string(crs_string)
    gpkg.set_crs(crs=crs_string)

    with gpkg.open_layer("polygon_feature") as src:
        assert not src.crs.is_geographic
        assert src.crs.to_epsg() == proj.to_epsg()
        assert src.crs == proj


def test_pixel_projection(gpkg: GeopackageDatabase):
    """
    Create a GeoPackage with no set projection
    """
    gpkg.set_crs("CRITICALMAAS:pixel")

    with gpkg.open_layer("polygon_feature") as src:
        log.debug(src.crs.to_dict())
        assert src.crs.to_epsg() is None
