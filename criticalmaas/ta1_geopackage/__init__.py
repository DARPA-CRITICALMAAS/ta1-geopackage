from pathlib import Path
from sqlalchemy import event
from sqlalchemy.engine import Engine
from macrostrat.database import Database
from fiona.crs import CRS
from warnings import warn
import fiona

from macrostrat.utils import get_logger

log = get_logger(__name__)


class GeopackageDatabase(Database):
    """
    A GeoPackage database with a pre-defined schema for CriticalMAAS TA1 outputs
    """

    file: Path

    def __init__(self, filename: Path | str, **kwargs):
        self.file = Path(filename)
        file_exists = self.file.exists()
        should_create = kwargs.pop("create", not file_exists)
        should_automap = kwargs.pop("automap", True)
        crs = kwargs.pop("crs", None)

        url = "sqlite:///" + str(filename)
        super().__init__(url, **kwargs)
        _enable_foreign_keys(self.engine)
        if should_create:
            if crs is None:
                warn(
                    "No CRS specified, using EPSG:4326 by default. Please specifiy a CRS or CRITICALMAAS:0 for pixels."
                )
                crs = "EPSG:4326"
            self.create_fixtures(crs=crs)

        file_exists = self.file.exists()
        if file_exists and should_automap:
            self.automap()

    def create_fixtures(self, *, crs: any = "EPSG:4326"):
        log.debug(f"Creating fixtures for {self.file}")

        fixtures = Path(__file__).parent / "fixtures"
        files = sorted(fixtures.glob("*.sql"))

        for file in files:
            self.run_sql(file, raise_errors=True)

        if crs is not None:
            self.set_crs(crs)

    def open(self, *, mode: str = "r", **kwargs):
        return fiona.open(
            str(self.file),
            mode=mode,
            driver="GPKG",
            PRELUDE_STATEMENTS="PRAGMA foreign_keys = ON",
            **kwargs,
        )

    def open_layer(self, layer: str, mode: str = "r", **kwargs):
        return self.open(
            layer=layer,
            mode=mode,
            **kwargs,
        )

    def write_features(self, layer: str, features, **kwargs):
        with self.open_layer(layer, "a", **kwargs) as src:
            src.writerecords(features)

    def set_crs(self, crs: any = None):
        _procedures = Path(__file__).parent / "procedures"
        srs_id = 0
        if crs not in PIXEL_COORDINATE_SYSTEMS:
            crs = CRS.from_user_input(crs)
            srs_id = crs.to_epsg()

            self.run_sql(
                _procedures / "insert-srid.sql",
                params={
                    "srs_name": crs["init"],
                    "srs_id": srs_id,
                    "organization": crs["init"].split(":")[0],
                    "organization_coordsys_id": crs["init"].split(":")[1],
                    "definition": crs.to_wkt(),
                    "description": str(crs),
                },
                raise_errors=True,
            )
        else:
            srs_id = 0

        self.run_sql(
            _procedures / "update-geometry-columns.sql",
            params={"srs_id": srs_id},
            raise_errors=True,
        )

    ## Various helper functions ##

    def write_models(self, models: list):
        """Write a set of SQLAlchemy models to the database."""
        self.session.add_all(models)
        self.session.commit()

    def enum_values(self, enum_name: str):
        """Get the values of an enum type."""
        table_name = "enum_" + enum_name
        try:
            model = getattr(self.model, table_name)
        except AttributeError:
            raise ValueError(f"Enum type {enum_name} does not exist")

        query = self.session.query(model.name)
        # Insert the line types
        return set(query.all())


PIXEL_COORDINATE_SYSTEMS = ["CRITICALMAAS:pixel", "CRITICALMAAS:0", "0", 0]


def _enable_foreign_keys(engine: Engine):
    event.listen(engine, "connect", _fk_pragma_on_connect)


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")
