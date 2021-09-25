import numpy as np
import geopandas as gpd
import pandas as pd
import logging
from shapely.geometry import Polygon, LineString

from scripts.constants import (
    PROCESSED_MERGED_PATH,
    ROAD_TAG_FEATURE_NAME,
    FEATURE_DATA_PATH,
)


ADT_KNOWN_FEATURE = "adt_known"
ADT_FEATURE = "adt"
NUMBER_SURROUNDING_ROADS_FEATURE = "num_surrounding_roads"


def get_polygon_bounds_from_linestring(geometry: LineString, buffer=0.1) -> Polygon:
    x_min, y_min, x_max, y_max = geometry.bounds
    x_min -= buffer
    y_min -= buffer
    x_max += buffer
    y_max += buffer
    poly = Polygon(
        [(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min), (x_min, y_min)]
    )
    return poly


def get_number_of_surrounding_roads(
    geometry: LineString, df: gpd.GeoDataFrame, buffer=0.1
) -> int:
    polygon_geometry = get_polygon_bounds_from_linestring(geometry, buffer)
    intersection = df.intersects(polygon_geometry)
    return np.sum(intersection)


def main():
    data = gpd.read_file(PROCESSED_MERGED_PATH)
    logging.info("Extracting ADT information")
    data[ADT_KNOWN_FEATURE] = ~pd.isna(data.ADT) * 1
    data[ADT_FEATURE] = data.ADT.fillna(0.0)
    logging.info("One hot encoding OSM road tag")
    road_tags = pd.get_dummies(data[ROAD_TAG_FEATURE_NAME], drop_first=True)
    data_with_road_encoding = gpd.GeoDataFrame(
        {**data.to_dict(), **road_tags.to_dict()}
    )
    logging.info(
        "Getting the number of surrounding roads for each road. This will take a while."
    )
    data_with_road_encoding[
        NUMBER_SURROUNDING_ROADS_FEATURE
    ] = data_with_road_encoding.geometry.apply(
        lambda geom: get_number_of_surrounding_roads(geom, data_with_road_encoding)
    )
    data_with_road_encoding.to_file(FEATURE_DATA_PATH)


if __name__ == "__main__":
    main()
