/** Geopackage core definitions
  See: http://www.geopackage.org
  Also: https://github.com/realiii/fudgeo/blob/00e1aca4abfeee9eb5968f6cee2914f9d565b54c/fudgeo/geopkg.sql

  We don't implement tables that are not required for the CriticalMAAS spec (e.g., raster tiles)
*/

CREATE TABLE gpkg_spatial_ref_sys (
    srs_name                 TEXT    NOT NULL,
    srs_id                   INTEGER NOT NULL PRIMARY KEY,
    organization             TEXT    NOT NULL,
    organization_coordsys_id INTEGER NOT NULL,
    definition               TEXT    NOT NULL,
    description              TEXT
);


CREATE TABLE gpkg_contents (
    table_name  TEXT     NOT NULL PRIMARY KEY,
    data_type   TEXT     NOT NULL,
    identifier  TEXT UNIQUE,
    description TEXT              DEFAULT '',
    last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S.%fZ', 'now')),
    min_x       DOUBLE,
    min_y       DOUBLE,
    max_x       DOUBLE,
    max_y       DOUBLE,
    srs_id      INTEGER,
    CONSTRAINT fk_gc_r_srs_id
        FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys (srs_id)
);


CREATE TABLE gpkg_geometry_columns (
    table_name         TEXT    NOT NULL,
    column_name        TEXT    NOT NULL,
    geometry_type_name TEXT    NOT NULL,
    srs_id             INTEGER NOT NULL,
    z                  TINYINT NOT NULL,
    m                  TINYINT NOT NULL,
    CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name),
    CONSTRAINT uk_gc_table_name UNIQUE (table_name),
    CONSTRAINT fk_gc_tn FOREIGN KEY (table_name)
        REFERENCES gpkg_contents (table_name),
    CONSTRAINT fk_gc_srs FOREIGN KEY (srs_id)
        REFERENCES gpkg_spatial_ref_sys (srs_id)
);