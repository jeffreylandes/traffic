import geopandas as gpd
import pandas as pd
from logs import log

from scripts.constants import (
    PROCESSED_MERGED_PATH,
    ROAD_TAG_FEATURE_NAME,
    FEATURE_DATA_PATH,
)
from predictive.features.num_nearby_roads import get_num_nearby_roads


ADT_KNOWN_FEATURE = "adt_known"
ADT_FEATURE = "adt"
NUMBER_SURROUNDING_ROADS_FEATURE = "num_surrounding_roads"


def main():
    data = gpd.read_file(PROCESSED_MERGED_PATH)
    log.info("Extracting ADT information")
    data[ADT_KNOWN_FEATURE] = ~pd.isna(data.ADT) * 1
    data[ADT_FEATURE] = data.ADT.fillna(0.0)
    log.info("One hot encoding OSM road tag")
    road_tags = pd.get_dummies(data[ROAD_TAG_FEATURE_NAME], drop_first=True)
    data_with_road_encoding = gpd.GeoDataFrame(
        {**data.to_dict(), **road_tags.to_dict()}, crs="4326"
    )
    log.info(
        "Getting the number of surrounding roads for each road."
    )
    data_with_num_nearby_roads = get_num_nearby_roads(data_with_road_encoding)
    data_with_num_nearby_roads.to_file(FEATURE_DATA_PATH, index=False)


if __name__ == "__main__":
    main()
