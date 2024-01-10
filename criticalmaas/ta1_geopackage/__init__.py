from pathlib import Path
from sqlalchemy import event
from sqlalchemy.engine import Engine
from macrostrat.database import Database
from fiona.crs import CRS
import fiona


class GeopackageDatabase(Database):
    """
    A GeoPackage database with a pre-defined schema for CriticalMAAS TA1 outputs
    """

    file: Path

    def __init__(self, filename: Path | str, **kwargs):
        self.file = Path(filename)
        url = "sqlite:///" + str(filename)
        super().__init__(url, **kwargs)
        _enable_foreign_keys(self.engine)

    def create_fixtures(self, crs: any = None):
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

    def set_crs(self, crs: any):
        crs = CRS.from_user_input(crs)
        epsg_code = crs.to_epsg()
        _procedures = Path(__file__).parent / "procedures"
        update_srid = _procedures / "update-srid.sql"

        self.run_sql(
            update_srid,
            params={
                "srs_name": crs["init"],
                "srs_id": epsg_code,
                "organization": crs["init"].split(":")[0],
                "organization_coordsys_id": crs["init"].split(":")[1],
                "definition": crs.to_wkt(),
                "description": str(crs),
            },
            raise_errors=True,
        )


def _enable_foreign_keys(engine: Engine):
    event.listen(engine, "connect", _fk_pragma_on_connect)


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")
