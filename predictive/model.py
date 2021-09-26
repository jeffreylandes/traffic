import torch.nn as nn
from torch import matmul


class CNNBlock(nn.Module):

    def __init__(self, in_channels, out_channels, kernel_size, stride, padding):
        super(CNNBlock, self).__init__()

        self.cnn_layer = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )

    def forward(self, feature_map, adjacency_matrix):
        new_feature_map = self.cnn_layer(feature_map)
        return matmul(new_feature_map, adjacency_matrix)


class GraphCNN(nn.Module):

    def __init__(self, num_in_channels=2, num_out_channels=1):
        super(GraphCNN, self).__init__()

        self.first_layer = CNNBlock(num_in_channels, 4, 3, 1, 1)
        self.second_layer = CNNBlock(4, 8, 3, 1, 1)
        self.out_layer = nn.Sequential(
            nn.Conv2d(8, num_out_channels, 3, 1, 1),
            nn.ReLU()
        )

    def forward(self, x, adjacency_matrix, mask):
        feature_map = self.first_layer(x, adjacency_matrix)
        feature_map = self.second_layer(feature_map, adjacency_matrix)
        prediction = matmul(self.out_layer(feature_map), adjacency_matrix)
        return prediction * mask
