import torch.nn as nn


class GraphCNN(nn.Module):

    def __init__(self, num_in_channels=2, num_out_channels=1):
        super(GraphCNN, self).__init__()

        self.cnn_layers = nn.Sequential(
            nn.Conv2d(num_in_channels, 4, 3, 1, 1),
            nn.BatchNorm2d(4),
            nn.ReLU(),
            nn.Conv2d(4, 8, 3, 1, 1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.Conv2d(8, num_out_channels, 3, 1, 1),
            nn.ReLU()
        )

    def forward(self, x, adjacency_matrix, mask):
        prediction = self.cnn_layers(x)
        return prediction * mask
