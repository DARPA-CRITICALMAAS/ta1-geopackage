from pathlib import Path
from macrostrat.utils import working_directory
from . import create_geopackage


def tests_geopackage_file_creation(tmp_path: Path):
    """Create temporary geopackage file and check that it exists."""
    with working_directory(str(tmp_path)):
        create_geopackage("test.gpkg")
        assert Path("test.gpkg").exists()
