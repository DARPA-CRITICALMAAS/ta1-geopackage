from pathlib import Path
from typing import Optional
from warnings import warn

import fiona
from fiona.crs import CRS
from geopandas import GeoDataFrame
from macrostrat.database import Database
from macrostrat.utils import get_logger
from pandas import DataFrame, read_sql_table
from sqlalchemy import event
from sqlalchemy.engine import Engine

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

    def check_constraints(self, table_name: str):
        # Manually check foreign key constraints, raising error on failure
        with self.engine.connect() as conn:
            result = conn.exec_driver_sql(
                f"PRAGMA foreign_key_check({table_name})",
            )
            errors = result.fetchall()
            n_errors = len(errors)
            if n_errors > 0:
                raise ForeignKeyError(table_name, errors)
            log.info(f"Foreign key constraints passed for {table_name}")

    def get_dataframe(
        self, table: str, *, use_geopandas: Optional[bool] = None, **kwargs
    ):
        """Convenience method to get a dataframe (or GeoDataFrame) from a table in the database."""

        if use_geopandas is None:
            res = self.run_query(
                "SELECT count(*) FROM gpkg_contents WHERE table_name = :table_name",
                {"table_name": table},
            ).scalar()
            use_geopandas = res > 0

        if not use_geopandas:
            return read_sql_table(table, self.engine, **kwargs)

        return GeoDataFrame.from_file(self.file, layer=table, **kwargs)

    def write_dataframe(self, df: GeoDataFrame | DataFrame, table: str, **kwargs):
        """Write a dataframe to the database."""
        check_constraints = kwargs.pop("check_constraints", True)
        if isinstance(df, GeoDataFrame):
            kwargs.setdefault("driver", "GPKG")
            kwargs.setdefault("promote_to_multi", True)
            df.to_file(self.file, layer=table, mode="a", **kwargs)
        else:
            df.to_sql(table, self.engine, if_exists="append", index=False)
        if check_constraints:
            # We have to check the constraints ourselves sometimes
            self.check_constraints(table)


PIXEL_COORDINATE_SYSTEMS = ["CRITICALMAAS:pixel", "CRITICALMAAS:0", "0", 0]


def _enable_foreign_keys(engine: Engine):
    event.listen(engine, "connect", _fk_pragma_on_connect)


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")


class GeopackageError(ValueError):
    pass


class ForeignKeyError(GeopackageError):
    def __init__(self, table: str, errors: list[tuple[str, str, str]]):
        self.errors = errors
        self.table = table
        super().__init__("Foreign key constraints failed")
