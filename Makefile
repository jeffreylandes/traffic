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

prepare-data: check-env data/traffic/merged_processed.shp

.PHONY: check-env
