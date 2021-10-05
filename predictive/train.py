from collections import defaultdict
import os
import pandas as pd
from torch.utils.data import DataLoader
from torch.optim import Adam
import torch.nn as nn
import torch
from uuid import uuid4

from predictive.opt import opt
from predictive.dataset import TrafficData
from predictive.model import GraphCNN
from logs import log


TRAINING_STORAGE_DIR = "predictive/training"
TRAINING_PANDAS_DF_PATH = os.path.join(TRAINING_STORAGE_DIR, "training.csv")


def get_model_path(train_id, data_dir=TRAINING_STORAGE_DIR):
    return os.path.join(data_dir, f"{train_id}.pth")


def save_model_details(train_id, parameters, losses):
    parameters_dict = vars(parameters)
    training_details = {
        "train_id": train_id,
        **parameters_dict,
        **losses,
        "final_validation_loss": losses["epoch_validation_losses"][-1]
    }

    df = pd.read_csv(TRAINING_PANDAS_DF_PATH) if os.path.exists(TRAINING_PANDAS_DF_PATH) else pd.DataFrame()
    df = df.append(training_details, ignore_index=True)
    df.to_csv(TRAINING_PANDAS_DF_PATH)


def train():
    train_id = str(uuid4())[:8]

    torch.set_default_dtype(torch.float32)

    model = GraphCNN()

    criterion = nn.L1Loss()
    optimizer = Adam(model.parameters(), lr=opt.lr)

    train_data = TrafficData()
    log.info(f"Number of training samples: {len(train_data)}")
    train_data_loader = DataLoader(train_data, batch_size=opt.batch_size, shuffle=True)

    validation_data = TrafficData(group="validation")
    log.info(f"Number of validation samples: {len(validation_data)}")
    validation_data_loader = DataLoader(validation_data, batch_size=1, shuffle=True)

    losses = defaultdict(list)

    for epoch in range(opt.num_epochs):
        model.train()
        log.info(f"Starting epoch {epoch}")
        train_epoch_loss = 0
        validation_epoch_loss = 0

        for step, data_item in enumerate(train_data_loader):
            feature_matrix = data_item["features"][0]
            adjacency_matrix = data_item["adjacency"][0]
            targets = data_item["targets"][0]
            mask = data_item["mask"][0]

            prediction = model(feature_matrix, adjacency_matrix, mask)

            optimizer.zero_grad()

            loss = criterion(prediction, targets)
            loss.backward()
            optimizer.step()

            train_epoch_loss += loss.item()

        with torch.no_grad():
            model.eval()
            for step, data_item in enumerate(validation_data_loader):
                feature_matrix = data_item["features"][0]
                adjacency_matrix = data_item["adjacency"][0]
                targets = data_item["targets"][0]
                mask = data_item["mask"][0]

                prediction = model(feature_matrix, adjacency_matrix, mask)
                loss = criterion(prediction, targets)
                validation_epoch_loss += loss.item()

        log.info(f"Total training loss for epoch {epoch}: {round(train_epoch_loss, 4)}")
        log.info(f"Total validation loss per batch for epoch {epoch}: {round(validation_epoch_loss, 4)}")
        losses["epoch_train_losses"].append(train_epoch_loss)
        losses["epoch_validation_losses"].append(validation_epoch_loss)

    torch.save(model.state_dict(), get_model_path(train_id))
    save_model_details(train_id, opt, losses)


if __name__ == "__main__":
    train()
