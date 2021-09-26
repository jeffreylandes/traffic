from torch.utils.data import DataLoader
from torch.optim import Adam
import torch.nn as nn
import torch

from predictive.data import TrafficData
from predictive.model import GraphCNN


def train():

    torch.set_default_dtype(torch.float32)

    model = GraphCNN()

    criterion = nn.L1Loss()
    optimizer = Adam(model.parameters(), lr=0.001)

    data = TrafficData()
    data_loader = DataLoader(data, batch_size=5, shuffle=True)

    for epoch in range(10):
        print(f"Starting epoch {epoch}")

        for step, data_item in enumerate(data_loader):
            feature_matrix = data_item["features"]
            adjacency_matrix = data_item["adjacency"]
            targets = data_item["targets"]
            mask = data_item["mask"]

            prediction = model(feature_matrix, adjacency_matrix, mask)

            optimizer.zero_grad()

            loss = criterion(prediction, targets)
            loss.backward()
            optimizer.step()
