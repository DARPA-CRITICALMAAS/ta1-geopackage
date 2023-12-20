CREATE TABLE enum_provenance_type (
  name TEXT PRIMARY KEY -- name of the provenance type
);

INSERT INTO enum_provenance_type (name) VALUES
  ('ground truth'),
  ('human verified'),
  ('human modified'),
  ('modelled'),
  ('raw data'),
  ('not processed');


CREATE TABLE enum_polygon_type (
  name TEXT PRIMARY KEY -- name of the polygon type
);

INSERT INTO enum_polygon_type (name) VALUES
  ('geologic unit'),
  ('tailings'),
  ('outcrop'),
  ('body of water'),
  ('other'),
  ('unknown');

CREATE TABLE enum_line_type (
  name TEXT PRIMARY KEY -- name of the line type
);

INSERT INTO enum_line_type (name) VALUES
  ('anticline'),
  ('antiform'),
  ('normal fault'),
  ('reverse fault'),
  ('thrust fault'),
  ('left-lateral strike-slip fault'),
  ('right-lateral strike-slip fault'),
  ('strike-slip fault'),
  ('fault'),
  ('lineament'),
  ('scarp'),
  ('syncline'),
  ('synform'),
  ('bed'),
  ('crater'),
  ('caldera'),
  ('dike'),
  ('escarpment'),
  ('fold'),
  ('other'),
  ('unknown');

CREATE TABLE enum_line_polarity (
  value TINYINT PRIMARY KEY -- for internal linking purposes in this file
);

INSERT INTO enum_line_polarity (value) VALUES
  (1), -- positive
  (-1), -- negative
  (0); -- undirected


CREATE TABLE enum_point_type (
  name TEXT PRIMARY KEY -- name of the point type
);

INSERT INTO enum_point_type (name) VALUES
  ('bedding'),
  ('foliation'),
  ('lineation'),
  ('joint'),
  ('fault'),
  ('fracture'),
  ('fold axis'),
  ('sample location'),
  ('outcrop'),
  ('mine site'),
  ('contact'),
  ('cleavage'),
  ('other'),
  ('unknown');

/** Extraction identifiers are used to link extractions to the model that produced them. */

CREATE TABLE enum_table_name (
  name TEXT PRIMARY KEY -- name of the model
);

INSERT INTO enum_table_name (name) VALUES
  ('geologic_unit'),
  ('polygon_feature'),
  ('polygon_type'),
  ('line_feature'),
  ('line_type'),
  ('point_feature'),
  ('point_type'),
  ('cross_section'),
  ('map_metadata'),
  ('projection_info');
