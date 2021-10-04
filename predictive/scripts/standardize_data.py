import geopandas as gpd
import numpy as np

from constants import FEATURE_DATA_PATH, STANDARDIZED_FEATURE_DATA_PATH


def standardize(col):
    return (col - np.mean(col)) / np.std(col)


def main():
    data = gpd.read_file(FEATURE_DATA_PATH)
    data['num_nearby'] = standardize(data['num_nearby'])
    data['adt_1'] = standardize(data['adt_1'])
    data.to_file(STANDARDIZED_FEATURE_DATA_PATH)


if __name__ == "__main__":
    main()
