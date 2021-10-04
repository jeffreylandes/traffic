import geopandas as gpd
from geopandas.tools import sjoin
from constants import OSM_GEOJSON_PATH, OSM_TRAFFIC_INITIAL_MERGE_PATH


def main():
    # Load OSM roads and reproject geometry
    osm_roads = gpd.read_file(OSM_GEOJSON_PATH)
    osm_roads = osm_roads.to_crs("EPSG:26915")
    osm_roads["osm_geometry"] = osm_roads["geometry"].astype(str)

    # Load traffic points and buffer geometry
    traffic_points = gpd.read_file(
        "data/traffic/Annual_Average_Daily_Traffic_Locations_in_Minnesota.shp"
    )
    print(f"There are {len(traffic_points)} traffic points.")
    traffic_points["original_geometry"] = traffic_points.geometry.astype(str)
    traffic_points["geometry"] = traffic_points.buffer(15)
    intersection = sjoin(traffic_points, osm_roads, how="left")
    intersection.to_file(OSM_TRAFFIC_INITIAL_MERGE_PATH)


if __name__ == "__main__":
    main()
