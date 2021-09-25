from yoyo import step


__depends__ = {"postgresql_extensions"}


steps = [
    step(
        """
        CREATE TABLE traffic (id INT, street_name VARCHAR(20));
        """,
        "drop table traffic",
    ),
    step(
        """
        select AddGeometryColumn('traffic', 'geometry', 4326, 'POINT', 2);
        alter table traffic alter column geometry SET NOT NULL;
        """,
        "alter table traffic drop geometry",
    ),
]
