data/osm/minnesota_roads.geojson:
	echo "Getting OSM road data for Minnesota based on pre-specified bounds"
	python scripts/minnesota_osm.py

data/traffic/merged_raw.shp: data/osm/minnesota_roads.geojson
	echo "Merging traffic points and OSM roads based on buffered traffic points"
	python scripts/merge_roads_traffic_points.py