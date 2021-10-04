from torch.utils.data import Dataset
import numpy as np
from math import ceil
import h5py

from predictive.scripts.process_data import FEATURE_COLUMNS


ADJACENCY_PATH = "adjacency.npy"
FEATURE_PATH = "features.npy"
TARGETS_PATH = "targets.npy"
PERCENTAGE_TARGETS_TO_MASK = 0.1
ADT_KNOWN_FEATURE_INDEX = FEATURE_COLUMNS.index("adt_known")
ADT_FEATURE_INDEX = FEATURE_COLUMNS.index("adt_1")


def add_axis(array: np.ndarray) -> np.ndarray:
    return np.expand_dims(array, axis=0)


class TrafficData(Dataset):
    def __init__(self, path="predictive/data/v3/v3.hdf5", group="train"):
        self.h5_file = h5py.File(path, "r")
        self.data = self.h5_file[group]

    def __len__(self):
        return self.data["targets"].shape[0] - 1

    def __getitem__(self, item):

        adjacency_matrix = self.data["adjacency"][item]
        feature_matrix = self.data["features"][item]
        targets = self.data["targets"][item][:, 0]

        targets_non_zero_adt = np.where(targets != 0)[0]
        num_targets_to_mask = ceil(
            PERCENTAGE_TARGETS_TO_MASK * len(targets_non_zero_adt)
        )
        num_targets_to_mask = max(num_targets_to_mask, 1)
        indices_to_mask = np.random.choice(
            targets_non_zero_adt, num_targets_to_mask, replace=False
        )

        # Change all the ADT values for points in the graph to 0 (if masked)
        for index in indices_to_mask:
            feature_matrix[index][ADT_FEATURE_INDEX] = 0.0
            feature_matrix[index][ADT_KNOWN_FEATURE_INDEX] = 0.0
        # Get indices of non-masked target values
        non_masked_indices = [
            i for i in range(len(targets)) if i not in indices_to_mask
        ]
        # Set them to 0 in the target
        targets[non_masked_indices] = 0

        assert adjacency_matrix.shape[0] == feature_matrix.shape[0]

        node_degrees = np.sum(adjacency_matrix, axis=0)
        diagonal_matrix = np.zeros_like(adjacency_matrix)
        np.fill_diagonal(diagonal_matrix, node_degrees)

        mask = np.zeros_like(targets)
        mask[np.where(targets) != 0] = 1

        data_item = {
            "adjacency": adjacency_matrix.astype(np.float32),
            "features": feature_matrix.astype(np.float32),
            "targets": targets.astype(np.float32),
            "mask": mask.astype(np.float32),
        }

        return data_item
