from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE EXTENSION IF NOT EXISTS "postgis";
        """
    )
]
