import geopandas as gpd
from sqlalchemy import create_engine

from constants import PROCESSED_MERGED_PATH


def main():

    data = gpd.read_file(PROCESSED_MERGED_PATH)

    # TODO: Should avoid this by cleaning up feature names early in the data processing workflow
    final_data = data.copy()
    final_data['adt'] = final_data['ADT'].copy()
    del final_data['ADT']
    del final_data['road_tag']

    engine = create_engine("postgresql://postgres:postgres@localhost/traffic")

    final_data.to_postgis(name="traffic", con=engine, if_exists="append")


if __name__ == "__main__":
    main()
