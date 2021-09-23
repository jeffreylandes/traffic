data/traffic/minnesota_traffic.zip:
	echo "Downloading traffic values"
	python scripts/minnesota_traffic.py


data/traffic/Annual_Average_Daily_Traffic_Locations_in_Minnesota.shp: data/traffic/minnesota_traffic.zip
	echo "Unzipping traffic values"
	unzip data/traffic/minnesota_traffic.zip -d data/traffic


data/osm/minnesota_roads.geojson: data/traffic/Annual_Average_Daily_Traffic_Locations_in_Minnesota.shp
	echo "Getting OSM road data for Minnesota based on pre-specified bounds"
	python scripts/minnesota_osm.py

data/traffic/merged_raw.shp: data/osm/minnesota_roads.geojson
	echo "Merging traffic points and OSM roads based on buffered traffic points"
	python scripts/merge_roads_traffic_points.py

data/traffic/merged_processed.shp: data/traffic/merged_raw.shp
	echo "Selecting the best batch for intersecting traffic points, based on OSM highway priority"
	python scripts/select_best_match.py

data/traffic/final_processed.shp: data/traffic/merged_processed.shp
	echo "Joining back with osm roads to get linestring geometry"
	python scripts/rejoin_osm.py

data/graphs/road_graph_network.pickle: data/traffic/final_processed.shp
	echo "Creating a network graph from the road dataset"
	python scripts/construct_graph.py

prepare-data: check-env data/graphs/road_graph_network.pickle

.PHONY: check-env
