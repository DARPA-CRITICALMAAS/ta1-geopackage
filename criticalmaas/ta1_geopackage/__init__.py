from pathlib import Path
from sqlalchemy import create_engine
from macrostrat.database.utils import run_sql
from sqlalchemy import event
from sqlalchemy.engine import Engine


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")


def enable_foreign_keys(engine: Engine):
    event.listen(engine, "connect", _fk_pragma_on_connect)


def create_geopackage(filename: Path | str):
    url = "sqlite:///" + str(filename)
    engine = create_engine(url)

    enable_foreign_keys(engine)

    fixtures = Path(__file__).parent / "fixtures"
    files = sorted(fixtures.glob("*.sql"))

    for file in files:
        run_sql(engine, file, raise_errors=True)

    return engine
