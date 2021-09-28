from torch.utils.data import DataLoader
from torch.optim import Adam
import torch.nn as nn
import torch

from predictive.dataset import TrafficData
from predictive.model import GraphCNN


def train():

    torch.set_default_dtype(torch.float32)

    model = GraphCNN()
    model.train()

    criterion = nn.L1Loss()
    optimizer = Adam(model.parameters(), lr=0.001)

    data = TrafficData()
    print(f"Number of samples: {len(data)}")
    data_loader = DataLoader(data, batch_size=1, shuffle=True)

    for epoch in range(10):
        print(f"Starting epoch {epoch}")
        epoch_loss = 0

        for step, data_item in enumerate(data_loader):
            feature_matrix = data_item["features"][0]
            adjacency_matrix = data_item["adjacency"][0]
            targets = data_item["targets"][0]
            mask = data_item["mask"][0]

            prediction = model(feature_matrix, adjacency_matrix, mask)

            optimizer.zero_grad()

            loss = criterion(prediction, targets)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        print(f"Loss for epoch {epoch}: {round(epoch_loss, 4)}")


if __name__ == "__main__":
    train()
