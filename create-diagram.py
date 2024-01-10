from criticalmaas.ta1_geopackage import GeopackageDatabase
from sadisplay import describe, render
from sqlalchemy import MetaData
from pathlib import Path
from sys import argv
from subprocess import run


def schema_for_table(table):
    """Create a fake schema in order to get sadisplay to render the the table in the correct groups"""
    if table.name == "map":
        return "map"
    if table.name == "map_metadata":
        return "map"
    if table.name.startswith("enum_"):
        return "enum"
    if table.name.startswith("gpkg_"):
        return "gpkg"
    for type in ["line", "point", "polygon"]:
        if table.name.startswith(type):
            return "extractions"
    if table.name == "geologic_unit":
        return "extractions"
    return None


outfile = Path(argv[1])

pkg = outfile.with_suffix(".gpkg")
pkg.unlink(missing_ok=True)

dotfile = outfile.with_suffix(".dot")
dotfile.unlink(missing_ok=True)

db = GeopackageDatabase(pkg)

meta = MetaData()
meta.reflect(bind=db.engine)

desc = describe(db.engine.url)

table_names = set(meta.tables.keys())

tables = []
for table in table_names:
    tbl = meta.tables[table]
    # Patch for sadisplay bug
    tbl.schema = schema_for_table(tbl)

    if tbl.name == "geometry_columns":
        # this is a duplicate table
        continue

    if tbl.name.startswith("enum_"):
        continue

    tables.append(tbl)

desc = describe(tables, default_schema="gpkg")

output = render.dot(desc)

with dotfile.open("w") as f:
    f.write(output)

run(["dot", "-Tpng", "-o", str(outfile), str(dotfile)])
