import os


ROAD_TAG_FEATURE_NAME = os.getenv("ROAD_TAG", "road_tag")
OSM_GEOJSON_PATH = os.getenv("OSM_GEOJSON_PATH", "data/osm/minnesota_roads.geojson")
PROCESSED_MERGED_PATH = os.getenv(
    "PROCESSED_MERGED_PATH", "data/traffic/final_processed.shp"
)
OSM_TRAFFIC_FILTERED_MERGE_PATH = os.getenv(
    "TRAFFIC_OSM_SELECTION_PATH", "data/osm/minnesota_roads.geojson"
)
OSM_TRAFFIC_INITIAL_MERGE_PATH = os.getenv(
    "OSM_TRAFFIC_INITIAL_MERGE_PATH", "data/traffic/merged_raw.shp"
)
TRAFFIC_ZIP_PATH = os.getenv("TRAFFIC_ZIP_PATH", "data/traffic/minnesota_traffic.zip")
TRAFFIC_URL = os.getenv(
    "TRAFFIC_URL",
    "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dot/trans_aadt_traffic_count_locs/shp_trans_aadt_traffic_count_locs.zip",
)
FEATURE_DATA_PATH = os.getenv("FEATURE_DATA_PATH", "data/ml/initial_feature_data.shp")
ADT_KNOWN_FEATURE = os.getenv("ADT_KNOWN_FEATURE", "adt_known")
ADT_FEATURE = os.getenv("ADT_FEATURE", "adt")
NUMBER_SURROUNDING_ROADS_FEATURE = os.getenv("NUMBER_SURROUNDING_ROADS_FEATURE", "num_surrounding_roads")
