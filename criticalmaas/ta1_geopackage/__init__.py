from pathlib import Path
from sqlalchemy import create_engine
from macrostrat.database.utils import run_sql
from sqlalchemy import event


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")


def create_geopackage(filename: Path | str):
    url = "sqlite:///" + str(filename)
    engine = create_engine(url)

    event.listen(engine, "connect", _fk_pragma_on_connect)
    # event.listen(engine, "connect", load_spatialite_gpkg)

    fixtures = Path(__file__).parent / "fixtures"
    files = sorted(fixtures.glob("*.sql"))

    for file in files:
        run_sql(engine, file, raise_errors=True)

    return engine
