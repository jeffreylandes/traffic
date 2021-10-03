import torch.nn as nn
import torch
import math


class GraphBlock(nn.Module):
    def __init__(self, in_dimensions, out_dimension, bias=True):
        super(GraphBlock, self).__init__()
        self.bias = None
        if bias:
            self.bias = nn.Parameter(
                torch.FloatTensor(out_dimension), requires_grad=True
            )
        self.weights = nn.Parameter(
            torch.FloatTensor(in_dimensions, out_dimension), requires_grad=True
        )
        self.reset_parameters()

    # TODO: Flexible wrt batch size
    def forward(self, feature_map, adjacency_matrix):
        new_feature_map = torch.mm(feature_map, self.weights)
        new_feature_map = torch.spmm(adjacency_matrix, new_feature_map)
        if self.bias is not None:
            new_feature_map = new_feature_map + self.bias
        return new_feature_map

    def reset_parameters(self):
        stdv = 1.0 / math.sqrt(self.weights.size(1))
        self.weights.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)


class GraphCNN(nn.Module):
    def __init__(self, num_in_dimensions=12, num_out_dimensions=1):
        super(GraphCNN, self).__init__()

        self.graph_block_1 = GraphBlock(num_in_dimensions, 6)
        self.graph_block_2 = GraphBlock(6, num_out_dimensions)

    def forward(self, x, adjacency_matrix, mask):
        feature_map = self.graph_block_1(x, adjacency_matrix)
        feature_map = self.graph_block_2(feature_map, adjacency_matrix)
        feature_map = torch.squeeze(feature_map)
        return feature_map * mask
