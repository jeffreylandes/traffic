from torch.utils.data import Dataset
import os
import numpy as np
from scipy.linalg import sqrtm

from predictive.process_data import MAX_ROAD_NETWORK_SIZE


ADJACENCY_PATH = "adjacency.npy"
FEATURE_PATH = "feature.npy"
TARGETS_PATH = "targets.npy"


class TrafficData(Dataset):

    def __init__(self, data_dir="predictive/data/vTest"):
        self._ids = os.listdir(data_dir)
        self.cache_size = 300
        self.cache = {}

    def __len__(self):
        return len(self._ids)

    def __getitem__(self, item):

        if item in self.cache:
            return self.cache[item]

        item_dir = self._ids[item]
        adjacency_matrix = np.load(os.path.join(item_dir, ADJACENCY_PATH))
        feature_matrix = np.load(os.path.join(item_dir, FEATURE_PATH))
        targets = np.load(os.path.join(item_dir, TARGETS_PATH))
        assert adjacency_matrix.shape == feature_matrix.shape

        node_degrees = np.sum(adjacency_matrix, axis=0)
        diagonal_matrix = np.zeros_like(adjacency_matrix)
        np.fill_diagonal(diagonal_matrix, node_degrees)

        sqrt_adjacency_matrix = sqrtm(adjacency_matrix)
        adjacency_matrix_standardized = np.dot(sqrt_adjacency_matrix, sqrt_adjacency_matrix) - adjacency_matrix

        adjacency_matrix_processed = np.zeros((MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE))
        feature_matrix_processed = np.zeros((MAX_ROAD_NETWORK_SIZE, MAX_ROAD_NETWORK_SIZE))
        adjacency_matrix_processed[:adjacency_matrix.shape[0], :adjacency_matrix.shape[1]] = adjacency_matrix_standardized
        feature_matrix_processed[:feature_matrix.shape[0], :feature_matrix.shape[1]] = feature_matrix

        mask = np.zeros_like(targets)
        mask[np.where(targets) != 0] = 1

        data_item = {
            "adjacency": adjacency_matrix_processed,
            "features": feature_matrix_processed,
            "targets": targets,
            "mask": mask
        }

        if len(self.cache) < self.cache_size:
            self.cache[item] = data_item
        else:
            self.cache.popitem()
            self.cache[item] = data_item

        return data_item
