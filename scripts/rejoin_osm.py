import geopandas as gpd
import numpy as np

from constants import (
    ROAD_TAG_FEATURE_NAME,
    OSM_GEOJSON_PATH,
    PROCESSED_MERGED_PATH,
    OSM_TRAFFIC_FILTERED_MERGE_PATH,
)


FINAL_COLUMNS = {
    "id": "osm_id",
    "CURRENT_VO": "adt",
}


def get_mean_adt(df: gpd.GeoDataFrame):
    mean_adt = np.mean(df['adt'])
    df.iloc[0]["adt"] = mean_adt
    return df.iloc[0]


def main():
    original_osm_roads = gpd.read_file(OSM_GEOJSON_PATH)
    traffic_counts = gpd.read_file(OSM_TRAFFIC_FILTERED_MERGE_PATH)
    original_osm_roads["osm_geometry"] = original_osm_roads["geometry"]
    merged_roads = original_osm_roads.merge(traffic_counts, how="left", on="id")
    merged_roads["geometry"] = merged_roads["geometry_x"]
    merged_roads.rename(columns=FINAL_COLUMNS, inplace=True)
    selected_columns = merged_roads[["osm_id", "adt", "geometry", ROAD_TAG_FEATURE_NAME]]
    selected_columns.groupby("osm_id")
    mean_adt_per_osm = selected_columns.groupby("osm_id").apply(
        lambda osm_id: get_mean_adt(osm_id)
    )
    mean_adt_per_osm = mean_adt_per_osm[selected_columns.columns]
    gpd.GeoDataFrame(mean_adt_per_osm).to_file(PROCESSED_MERGED_PATH, index=False)


if __name__ == "__main__":
    main()
