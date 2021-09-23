import geopandas as gpd
from scripts.minnesota_osm import OSM_HIGHWAY_PRIORITY
from collections import defaultdict
import numpy as np
from scripts.constants import ROAD_TAG_FEATURE_NAME


def select_best_match(intersection: gpd.GeoDataFrame):
    if len(intersection) == 1:
        return intersection
    reversed_priorities = defaultdict(list)
    for index, row in intersection.iterrows():
        priority = OSM_HIGHWAY_PRIORITY[row[ROAD_TAG_FEATURE_NAME]]
        reversed_priorities[priority].append(index)
    highest_priority = np.min(list(reversed_priorities.keys()))
    matches = reversed_priorities[highest_priority]
    magic_match_index = matches[0]
    return intersection.loc[magic_match_index]


def main():
    merged_osm_traffic = gpd.read_file("data/traffic/raw_intersection_15.shp")
    best_match = merged_osm_traffic.groupby("SEQUENCE_N").apply(lambda intersection: select_best_match(intersection))
    best_match = best_match[merged_osm_traffic.columns]
    del best_match[ROAD_TAG_FEATURE_NAME]
    best_match.to_file("data/traffic/merged_processed.shp", index=False)


if __name__ == "__main__":
    main()
