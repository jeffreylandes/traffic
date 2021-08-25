from osmxtract import overpass
from osmxtract.errors import OverpassTooManyRequests
import geopandas as gpd
import numpy as np
from typing import Tuple
import pandas as pd
import time


OUT_PATH = "data/osm/minnesota_roads.shp"
NUM_TILES = 5
target_values = [
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "residential",
        "motorway_link",
        "trunk_link",
        "primary_link",
        "secondary_link",
        "tertiary_link"
    ]


def make_request(bounds: Tuple[float, float, float, float], attempt: int = 0):
    if attempt > 10:
        raise Exception("Too many requests.")
    try:
        query = overpass.ql_query(
            bounds,
            tag="highway",
            values=target_values
        )
        response = overpass.request(query)
        return response
    except OverpassTooManyRequests:
        print("Too many requests. Waiting 10 seconds before retrying.")
        time.sleep(10)
        return make_request(bounds, attempt + 1)


def get_roads_from_bounds(bounds: Tuple[float, float, float, float]) -> gpd.GeoDataFrame:
    response = make_request(bounds)
    feature_collection = overpass.as_geojson(response, "linestring")
    print(f"Number of roads: {len(feature_collection['features'])}")
    road_data = gpd.GeoDataFrame(feature_collection["features"], crs="EPSG:4326")
    return road_data


def main():
    minnesota_bounds = (43.439, -97.384, 49.068, -89.466)
    x_min, y_min, x_max, y_max = minnesota_bounds
    x_stride = (x_max - x_min) / NUM_TILES
    y_stride = (y_max - y_min) / NUM_TILES
    all_roads = []
    for x_start in np.linspace(x_min, x_max, NUM_TILES):
        for y_start in np.linspace(y_min, y_max, NUM_TILES):
            x_end = x_start + x_stride
            y_end = y_start + y_stride
            bounds = (x_start, y_start, x_end, y_end)
            roads_iter = get_roads_from_bounds(bounds)
            all_roads.append(roads_iter)
    final_dataframe = gpd.GeoDataFrame(pd.concat(all_roads, ignore_index=True))
    final_dataframe.to_file(OUT_PATH)


if __name__ == "__main__":
    main()