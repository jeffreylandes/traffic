import geopandas as gpd
from scripts.constants import (
    ROAD_TAG_FEATURE_NAME,
    OSM_GEOJSON_PATH,
    PROCESSED_MERGED_PATH,
    OSM_TRAFFIC_FILTERED_MERGE_PATH,
)


FINAL_COLUMNS = {
    "id": "osm_id",
    "CURRENT_VO": "ADT",
}


def main():
    original_osm_roads = gpd.read_file(OSM_GEOJSON_PATH)
    traffic_counts = gpd.read_file(OSM_TRAFFIC_FILTERED_MERGE_PATH)
    original_osm_roads["osm_geometry"] = original_osm_roads["geometry"]
    merged_roads = original_osm_roads.merge(traffic_counts, how="left", on="id")
    merged_roads["geometry"] = merged_roads["geometry_x"]
    merged_roads.rename(columns=FINAL_COLUMNS, inplace=True)
    final_table = merged_roads[["osm_id", "ADT", "geometry", ROAD_TAG_FEATURE_NAME]]
    gpd.GeoDataFrame(final_table).to_file(PROCESSED_MERGED_PATH)


if __name__ == "__main__":
    main()
