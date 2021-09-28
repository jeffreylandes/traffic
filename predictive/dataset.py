from torch.utils.data import Dataset
import os
import numpy as np
from scipy.linalg import sqrtm
from math import ceil

from predictive.process_data import MAX_ROAD_NETWORK_SIZE, FEATURE_COLUMNS


ADJACENCY_PATH = "adjacency.npy"
FEATURE_PATH = "features.npy"
TARGETS_PATH = "targets.npy"
PERCENTAGE_TARGETS_TO_MASK = 0.1
ADT_KNOWN_FEATURE_INDEX = FEATURE_COLUMNS.index("adt_known")
ADT_FEATURE_INDEX = FEATURE_COLUMNS.index("adt_1")


def add_axis(array: np.ndarray) -> np.ndarray:
    return np.expand_dims(array, axis=0)


class TrafficData(Dataset):

    def __init__(self, data_dir="predictive/data/vTest"):
        self._ids = os.listdir(data_dir)
        self.data_dir = data_dir
        self.cache_size = 300
        self.cache = {}

    def __len__(self):
        return len(self._ids)

    def __getitem__(self, item):

        if item in self.cache:
            return self.cache[item]

        item_dir = self._ids[item]
        adjacency_matrix = np.load(os.path.join(self.data_dir, item_dir, ADJACENCY_PATH))
        feature_matrix = np.load(os.path.join(self.data_dir, item_dir, FEATURE_PATH))

        targets = np.load(os.path.join(self.data_dir, item_dir, TARGETS_PATH))
        targets_non_zero_adt = np.where(targets != 0)[0]
        num_targets_to_mask = ceil(PERCENTAGE_TARGETS_TO_MASK * len(targets_non_zero_adt))
        num_targets_to_mask = max(num_targets_to_mask, 1)
        indices_to_mask = np.random.choice(targets_non_zero_adt, num_targets_to_mask, replace=False)

        # Change all the ADT values for points in the graph to 0 (if masked)
        for index in indices_to_mask:
            feature_matrix[index][ADT_FEATURE_INDEX] = 0.0
            feature_matrix[index][ADT_KNOWN_FEATURE_INDEX] = 0.0
        # Get indices of non-masked target values
        non_masked_indices = [i for i in range(len(targets)) if i not in indices_to_mask]
        # Set them to 0 in the target
        targets[non_masked_indices] = 0

        assert adjacency_matrix.shape[0] == feature_matrix.shape[0]

        node_degrees = np.sum(adjacency_matrix, axis=0)
        diagonal_matrix = np.zeros_like(adjacency_matrix)
        np.fill_diagonal(diagonal_matrix, node_degrees)

        # May not be doing this correctly...
        sqrt_adjacency_matrix = sqrtm(adjacency_matrix)
        adjacency_matrix_standardized = np.dot(sqrt_adjacency_matrix, sqrt_adjacency_matrix) - adjacency_matrix

        adjacency_matrix_processed = np.zeros((MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE))
        feature_matrix_processed = np.zeros((MAX_ROAD_NETWORK_SIZE, len(FEATURE_COLUMNS)))
        targets_processed = np.zeros(MAX_ROAD_NETWORK_SIZE)
        adjacency_matrix_processed[:adjacency_matrix.shape[0], :adjacency_matrix.shape[1]] = adjacency_matrix_standardized
        feature_matrix_processed[:feature_matrix.shape[0], :feature_matrix.shape[1]] = feature_matrix
        targets_processed[:adjacency_matrix.shape[0]] = targets

        mask = np.zeros_like(targets_processed)
        mask[np.where(targets_processed) != 0] = 1

        data_item = {
            "adjacency": adjacency_matrix_processed.astype(np.float32),
            "features": feature_matrix_processed.astype(np.float32),
            "targets": targets_processed.astype(np.float32),
            "mask": mask.astype(np.float32)
        }

        if len(self.cache) < self.cache_size:
            self.cache[item] = data_item
        else:
            self.cache.popitem()
            self.cache[item] = data_item

        return data_item
