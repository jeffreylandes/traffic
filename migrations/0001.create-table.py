from yoyo import step


__depends__ = {"0002.extensions"}


steps = [
    step(
        "CREATE TABLE traffic (osm_id INT, adt FLOAT, PRIMARY KEY (osm_id))",
        "DROP TABLE traffic"
    ),
    step(
        "SELECT AddGeometryColumn('traffic', 'geometry', 4326, 'LINESTRING', 2)",
        "ALTER TABLE traffic drop geometry"
    )
]
