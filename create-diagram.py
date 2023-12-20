from criticalmaas.ta1_geopackage import create_geopackage
from sadisplay import describe, render
from sqlalchemy import MetaData
from pathlib import Path
from sys import argv
from subprocess import run

outfile = Path(argv[1])

pkg = outfile.with_suffix(".gpkg")
pkg.unlink(missing_ok=True)

dotfile = outfile.with_suffix(".dot")
dotfile.unlink(missing_ok=True)

engine = create_geopackage(pkg)
meta = MetaData()
meta.reflect(bind=engine)

desc = describe(engine.url)

table_names = set(meta.tables.keys())

tables = []
for table in table_names:
    tbl = meta.tables[table]
    # Patch for sadisplay bug
    tbl.schema = None
    tables.append(tbl)

desc = describe(tables, default_schema="gpkg")

output = render.dot(desc)

with dotfile.open("w") as f:
    f.write(output)

run(["dot", "-Tpng", "-o", str(outfile), str(dotfile)])
