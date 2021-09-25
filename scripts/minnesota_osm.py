from osmxtract import overpass
from osmxtract.errors import OverpassTooManyRequests
import geopandas as gpd
import numpy as np
from typing import Tuple
import pandas as pd
import time
import os
from scripts.constants import ROAD_TAG_FEATURE_NAME, OSM_GEOJSON_PATH


NUM_TILES = 5
OSM_HIGHWAY_PRIORITY = {
    "motorway": 0,
    "trunk": 2,
    "primary": 4,
    "secondary": 6,
    "tertiary": 8,
    "residential": 10,
    "motorway_link": 1,
    "trunk_link": 3,
    "primary_link": 5,
    "secondary_link": 7,
    "tertiary_link": 9
}
target_values = list(OSM_HIGHWAY_PRIORITY.keys())


def make_request(bounds: Tuple[float, float, float, float], attempt: int = 0):
    if attempt > 10:
        raise Exception("Too many requests.")
    try:
        print(f"Making a overpass request with bounds: {bounds}")
        query = overpass.ql_query(
            bounds,
            tag="highway",
            values=target_values
        )
        response = overpass.request(query)
        return response
    except OverpassTooManyRequests:
        print("Too many requests. Waiting 20 seconds before retrying.")
        time.sleep(20)
        return make_request(bounds, attempt + 1)


def get_roads_from_bounds(bounds: Tuple[float, float, float, float]) -> gpd.GeoDataFrame:
    response = make_request(bounds)
    feature_collection = overpass.as_geojson(response, "linestring")
    if len(feature_collection["features"]):
        response = make_request(bounds)
        feature_collection = overpass.as_geojson(response, "linestring")
    print(f"Number of roads: {len(feature_collection['features'])}")
    road_data = gpd.GeoDataFrame(feature_collection["features"], crs="EPSG:4326")
    return road_data


def main():
    minnesota_bounds = (43.439, -97.384, 49.068, -89.466)
    x_min, y_min, x_max, y_max = minnesota_bounds
    x_points = np.linspace(x_min, x_max, NUM_TILES)
    y_points = np.linspace(y_min, y_max, NUM_TILES)
    all_roads = []
    for x_index in range(len(x_points) - 1):
        for y_index in range(len(y_points) - 1):
            x_start = x_points[x_index]
            x_end = x_points[x_index + 1]
            y_start = y_points[y_index]
            y_end = y_points[y_index + 1]
            bounds = (x_start, y_start, x_end, y_end)
            roads_iter = get_roads_from_bounds(bounds)
            all_roads.append(roads_iter)
            break
        break
    final_dataframe = gpd.GeoDataFrame(pd.concat(all_roads, ignore_index=True))
    final_dataframe[ROAD_TAG_FEATURE_NAME] = final_dataframe.properties.apply(lambda row: row["highway"])
    final_dataframe.to_file(OSM_GEOJSON_PATH, driver="GeoJSON")


if __name__ == "__main__":
    main()