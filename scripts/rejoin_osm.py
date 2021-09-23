import geopandas as gpd
from scripts.constants import ROAD_TAG_FEATURE_NAME


FINAL_COLUMNS = {
    "id": "osm_id",
    "CURRENT_VO": "ADT",
}


def main():
    original_osm_roads = gpd.read_file("data/osm/minnesota_roads.geojson")
    traffic_counts = gpd.read_file("data/traffic/merged_processed.shp")
    original_osm_roads['osm_geometry'] = original_osm_roads['geometry']
    merged_roads = original_osm_roads.merge(traffic_counts, how="left", on="id")
    merged_roads['geometry'] = merged_roads['geometry_x']
    merged_roads.rename(columns=FINAL_COLUMNS, inplace=True)
    final_table = merged_roads[["osm_id", "ADT", "geometry", ROAD_TAG_FEATURE_NAME]]
    gpd.GeoDataFrame(final_table).to_file("data/traffic/final_processed.shp")


if __name__ == "__main__":
    main()