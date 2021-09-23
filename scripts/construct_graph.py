import networkx as nx
import geopandas as gpd
from geopandas.tools import sjoin
import os


def main():
    data = gpd.read_file("data/traffic/final_processed.shp")
    data_as_dict = data.to_dict('index')
    data_as_nodes_with_attributes = list(data_as_dict.items())

    self_intersections = sjoin(data, data, how="left")
    self_intersections['index_left'] = self_intersections.index
    self_intersections_filtered = self_intersections[self_intersections.index_left < self_intersections.index_right]
    edges = list(zip(self_intersections_filtered["index_left"].tolist(), self_intersections_filtered["index_right"].tolist()))

    graph = nx.Graph()
    graph.add_nodes_from(data_as_nodes_with_attributes)
    graph.add_edges_from(edges)
    if not os.path.exists("data/graphs"):
        os.mkdir("data/graphs")
    nx.write_gpickle(graph, "data/graphs/road_graph_network.pickle")


if __name__ == "__main__":
    main()
