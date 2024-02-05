from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from typing import Generator

from macrostrat.utils import get_logger
from pytest import fixture

from criticalmaas.ta1_geopackage import GeopackageDatabase
from criticalmaas.ta1_geopackage.test_utils import _write_test_types

log = get_logger(__name__)


@fixture(scope="session")
def _empty_gpkg() -> Generator[GeopackageDatabase, None, None]:
    with TemporaryDirectory() as tempdir:
        db = GeopackageDatabase(Path(tempdir) / "test.gpkg", crs="EPSG:4326")
        yield db


@fixture(scope="function")
def empty_gpkg(_empty_gpkg) -> Generator[GeopackageDatabase, None, None]:
    new_path = _empty_gpkg.file.with_name("empty.gpkg")
    copyfile(_empty_gpkg.file, new_path)
    new_gpkg = GeopackageDatabase(new_path)
    yield new_gpkg


@fixture(scope="session")
def _base_gpkg(
    _empty_gpkg: GeopackageDatabase,
) -> Generator[GeopackageDatabase, None, None]:
    new_path = _empty_gpkg.file.with_name("test-with-features.gpkg")
    copyfile(_empty_gpkg.file, new_path)

    new_gpkg = GeopackageDatabase(new_path)

    _write_test_types(new_gpkg)
    yield new_gpkg


@fixture(scope="function")
def gpkg(_base_gpkg: GeopackageDatabase) -> Generator[GeopackageDatabase, None, None]:
    new_path = _base_gpkg.file.with_name("test-current.gpkg")
    copyfile(_base_gpkg.file, new_path)
    new_gpkg = GeopackageDatabase(new_path)
    yield new_gpkg
    new_gpkg.file.unlink()
