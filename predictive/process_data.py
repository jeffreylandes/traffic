import geopandas as gpd
import numpy as np
from typing import Tuple, List, Optional
from shapely.geometry import Polygon
import pandas as pd
from geopandas.tools import sjoin
import networkx as nx

from scripts.constants import FEATURE_DATA_PATH


MAX_ROAD_NETWORK_SIZE = 100
MAX_STRIDE = 0.01
FEATURE_COLUMNS = [
    "adt_known", "adt", "motorway_link", "primary", "primary_link", "secondary_link", "tertiary", "tertiary_link",
    "trunk", "trunk_link", "num_surrounding_roads"
]

Bounds = Tuple[float, float, float, float]


def get_adjacency_matrix(data: gpd.GeoDataFrame) -> pd.DataFrame:
    data_as_dict = data.to_dict("index")
    data_as_nodes_with_attributes = list(data_as_dict.items())
    self_intersections = sjoin(data, data, how="left")
    self_intersections["index_left"] = self_intersections.index
    self_intersections_filtered = self_intersections[
        self_intersections.index_left < self_intersections.index_right
        ]
    edges = list(
        zip(
            self_intersections_filtered["index_left"].tolist(),
            self_intersections_filtered["index_right"].tolist(),
        )
    )

    graph = nx.Graph()
    graph.add_nodes_from(data_as_nodes_with_attributes)
    graph.add_edges_from(edges)
    adjacency_df = nx.convert_matrix.to_pandas_adjacency(graph)
    return adjacency_df


def get_feature_matrix(data: gpd.GeoDataFrame) -> pd.DataFrame:
    return data[FEATURE_COLUMNS]


def get_polygon_from_bounds(bounds: Bounds) -> Polygon:
    x_min, y_min, x_max, y_max = bounds
    return Polygon(
        [
            (x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min), (x_min, y_min)
        ]
    )


def split_bounds(bounds: Bounds) -> List[Bounds]:
    x_min, y_min, x_max, y_max = bounds
    x_mean = (x_max + x_min) / 2
    y_mean = (y_max + y_min) / 2
    first_quadrant = (x_min, y_min, x_mean, y_mean)
    second_quadrant = (x_min, y_mean, x_mean, y_max)
    third_quadrant = (x_mean, y_min, x_max, y_mean)
    fourth_quadrant = (x_mean, y_mean, x_max, y_max)
    return [
        first_quadrant, second_quadrant, third_quadrant, fourth_quadrant
    ]


def recursively_get_polygon_bounds(data: gpd.GeoDataFrame, bounds: Bounds) -> Optional[List[gpd.GeoDataFrame]]:
    polygon = get_polygon_from_bounds(bounds)
    intersection_indices = data.intersects(polygon)
    intersecting_dfs = []
    if np.sum(intersection_indices) > MAX_ROAD_NETWORK_SIZE:
        new_bounds = split_bounds(bounds)
        for b in new_bounds:
            intersecting_dfs.extend(recursively_get_polygon_bounds(data, b))
    elif np.sum(intersection_indices) == 0:
        return None
    return [
        data[intersection_indices]
    ]


def main():
    data = gpd.read_file(FEATURE_DATA_PATH)
    x_min, y_min, x_max, y_max = data.total_bounds

    for x in np.arange(x_min, x_max, MAX_STRIDE):
        for y in np.arange(y_min, y_max, MAX_STRIDE):
            bounds = (x, y, x + MAX_STRIDE, y + MAX_STRIDE)

            intersecting_dfs = recursively_get_polygon_bounds(data, bounds)
            if intersecting_dfs is None:
                continue

            for intersecting_df in intersecting_dfs:
                adj_matrix = get_adjacency_matrix(intersecting_df)
                feature_matrix = get_feature_matrix(intersecting_df)
