import geopandas as gpd
import numpy as np
from typing import Tuple, List, Optional
from shapely.geometry import Polygon
import pandas as pd
from geopandas.tools import sjoin
import networkx as nx
import os
from itertools import product
import h5py
from dataclasses import dataclass

from scripts.constants import FEATURE_DATA_PATH, ADT_KNOWN_FEATURE
from logs import log


VERSION = os.getenv("VERSION", "vTest")
MAX_ROAD_NETWORK_SIZE = 100
MAX_STRIDE = 1.0
TRAIN_VALIDATION_SPLIT = 0.9
FEATURE_COLUMNS = [
    "adt_known",
    "adt_1",
    "motorway_l",
    "primary",
    "primary_li",
    "secondary_",
    "tertiary",
    "tertiary_l",
    "trunk",
    "trunk_link",
    "residentia",
    "num_nearby",
]

Bounds = Tuple[float, float, float, float]


@dataclass
class H5Data:
    file: h5py.File
    validation_group: h5py.Group
    training_group: h5py.Group
    validation_adjacency_data: h5py.Dataset
    validation_features_data: h5py.Dataset
    validation_target_data: h5py.Dataset
    training_adjacency_data: h5py.Dataset
    training_features_data: h5py.Dataset
    training_target_data: h5py.Dataset


def create_hdf5_data(path: str) -> H5Data:
    h5_file = h5py.File(path, "w")

    training_group = h5_file.create_group("train")
    training_feature = training_group.create_dataset(
        "features",
        (1, MAX_ROAD_NETWORK_SIZE, len(FEATURE_COLUMNS)),
        maxshape=(None, MAX_ROAD_NETWORK_SIZE, len(FEATURE_COLUMNS)),
    )
    training_adjacency = training_group.create_dataset(
        "adjacency",
        (1, MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE),
        maxshape=(None, MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE),
    )
    training_targets = training_group.create_dataset(
        "targets",
        (1, MAX_ROAD_NETWORK_SIZE, 1),
        maxshape=(None, MAX_ROAD_NETWORK_SIZE, 1),
    )

    validation_group = h5_file.create_group("validation")
    validation_features = validation_group.create_dataset(
        "features",
        (1, MAX_ROAD_NETWORK_SIZE, len(FEATURE_COLUMNS)),
        maxshape=(None, MAX_ROAD_NETWORK_SIZE, len(FEATURE_COLUMNS)),
    )
    validation_adjacency = validation_group.create_dataset(
        "adjacency",
        (1, MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE),
        maxshape=(None, MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE),
    )
    validation_targets = validation_group.create_dataset(
        "targets",
        (1, MAX_ROAD_NETWORK_SIZE, 1),
        maxshape=(None, MAX_ROAD_NETWORK_SIZE, 1),
    )
    return H5Data(
        file=h5_file,
        validation_group=validation_group,
        training_group=training_group,
        validation_adjacency_data=validation_adjacency,
        validation_features_data=validation_features,
        validation_target_data=validation_targets,
        training_adjacency_data=training_adjacency,
        training_features_data=training_feature,
        training_target_data=training_targets,
    )


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
        [(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min), (x_min, y_min)]
    )


def split_bounds(bounds: Bounds) -> List[Bounds]:
    x_min, y_min, x_max, y_max = bounds
    x_mean = (x_max + x_min) / 2
    y_mean = (y_max + y_min) / 2
    first_quadrant = (x_min, y_min, x_mean, y_mean)
    second_quadrant = (x_min, y_mean, x_mean, y_max)
    third_quadrant = (x_mean, y_min, x_max, y_mean)
    fourth_quadrant = (x_mean, y_mean, x_max, y_max)
    return [first_quadrant, second_quadrant, third_quadrant, fourth_quadrant]


def recursively_get_polygon_bounds(
    data: gpd.GeoDataFrame, bounds: Bounds
) -> Optional[List[gpd.GeoDataFrame]]:
    polygon = get_polygon_from_bounds(bounds)
    intersection_indices = data.intersects(polygon)
    intersecting_dfs = []
    if np.sum(intersection_indices) > MAX_ROAD_NETWORK_SIZE:
        new_bounds = split_bounds(bounds)
        for b in new_bounds:
            recursive_intersecting_dfs = recursively_get_polygon_bounds(
                data[intersection_indices], b
            )
            if recursive_intersecting_dfs is not None:
                intersecting_dfs.extend(recursive_intersecting_dfs)
        return intersecting_dfs
    elif np.sum(intersection_indices) == 0:
        return None
    return [data[intersection_indices]]


def add_item_to_dataset(dataset: h5py.Dataset, item: np.ndarray):
    dataset[len(dataset) - 1, :item.shape[0], :item.shape[1]] = item
    dataset.resize((len(dataset) + 1, dataset.shape[1], dataset.shape[2]))


def main():
    data = gpd.read_file(FEATURE_DATA_PATH)
    log.info("Read data into memory.")
    x_min, y_min, x_max, y_max = data.total_bounds

    data_dir = f"predictive/data/{VERSION}"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    log.info("Beginning to create dataset.")
    xs = np.arange(x_min, x_max, MAX_STRIDE)
    ys = np.arange(y_min, y_max, MAX_STRIDE)
    xs_and_ys = product(xs, ys)

    h5_file = f"{VERSION}.hdf5"
    h5_data = create_hdf5_data(os.path.join(data_dir, h5_file))

    for x, y in xs_and_ys:
        bounds = (x, y, x + MAX_STRIDE, y + MAX_STRIDE)

        initial_polygon = get_polygon_from_bounds(bounds)
        data_within_polygon = data[data.within(initial_polygon)]
        if np.sum(data_within_polygon[ADT_KNOWN_FEATURE]) == 0:
            continue

        intersecting_dfs = recursively_get_polygon_bounds(data_within_polygon, bounds)
        if intersecting_dfs is None:
            continue

        for intersecting_df in intersecting_dfs:
            if np.sum(intersecting_df[ADT_KNOWN_FEATURE]) <= 1:
                continue
            adj_matrix = get_adjacency_matrix(intersecting_df).to_numpy()
            feature_matrix = get_feature_matrix(intersecting_df).to_numpy()
            targets = intersecting_df[ADT_KNOWN_FEATURE].to_numpy()
            targets = np.expand_dims(targets, axis=1)

            if np.random.rand() < TRAIN_VALIDATION_SPLIT:
                log.info("Adding item to training dataset")
                add_item_to_dataset(h5_data.training_adjacency_data, adj_matrix)
                add_item_to_dataset(h5_data.training_features_data, feature_matrix)
                add_item_to_dataset(h5_data.training_target_data, targets)
            else:
                add_item_to_dataset(h5_data.validation_adjacency_data, adj_matrix)
                add_item_to_dataset(h5_data.validation_features_data, feature_matrix)
                add_item_to_dataset(h5_data.validation_target_data, targets)
                log.info("Adding item to validation dataset")

    h5_data.file.close()


if __name__ == "__main__":
    main()
