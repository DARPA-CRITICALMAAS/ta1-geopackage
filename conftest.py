from pathlib import Path
from typing import Generator

from macrostrat.utils import get_logger, working_directory
from pytest import fixture

from criticalmaas.ta1_geopackage import GeopackageDatabase

log = get_logger(__name__)


@fixture(scope="function")
def gpkg(tmp_path: Path) -> Generator[GeopackageDatabase, None, None]:
    with working_directory(str(tmp_path)):
        db = GeopackageDatabase(tmp_path / "test.gpkg", crs="EPSG:4326")
        yield db
