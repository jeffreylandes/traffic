import geopandas as gpd
from sqlalchemy import create_engine

from constants import PROCESSED_MERGED_PATH


def main():

    data = gpd.read_file(PROCESSED_MERGED_PATH)

    engine = create_engine("postgresql://postgres:postgres@localhost/traffic")

    data.to_postgis(name="traffic", con=engine, if_exists="append")


if __name__ == "__main__":
    main()
