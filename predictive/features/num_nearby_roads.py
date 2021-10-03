import scipy.spatial as spatial
import numpy as np
import geopandas as gpd


BUFFER = 0.1


def get_num_nearby_roads(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    data["representative_point"] = data.representative_point()
    data["point_x"] = data["representative_point"].apply(lambda point: point.x)
    data["point_y"] = data["representative_point"].apply(lambda point: point.y)
    point_tree = spatial.cKDTree(data[["point_x", "point_y"]])
    data["num_nearby_roads"] = data.apply(
        lambda row: len(
            point_tree.query_ball_point(np.array([row["point_x"], row["point_y"]]), 0.1)
        ),
        axis=1,
    )
    del data["point_x"]
    del data["point_y"]
    del data["representative_point"]
    return data
