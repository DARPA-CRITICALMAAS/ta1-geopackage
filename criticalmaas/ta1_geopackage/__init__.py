from pathlib import Path
from sqlalchemy import create_engine
from macrostrat.database import run_sql


def create_geopackage(filename: Path | str):
    url = "sqlite:///" + str(filename)
    engine = create_engine(url)

    fixtures = Path(__file__).parent / "fixtures"
    files = sorted(fixtures.glob("*.sql"))

    for file in files:
        run_sql(engine, file)

    return engine
