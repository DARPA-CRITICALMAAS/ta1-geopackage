from pathlib import Path
from sqlalchemy import create_engine


def create_geopackage(filename: Path | str):
    url = "sqlite:///" + str(filename)
    db = create_engine(url)

    db.engine.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")

    return db
