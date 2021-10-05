import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--num_epochs', type=int, default=20)
parser.add_argument('--batch_size', type=int, default=1)
parser.add_argument('--lr', type=float, default=0.001)
parser.add_argument('--date', type=str, default=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
parser.add_argument('--data_version', type=str, default="vTest")

opt, _ = parser.parse_known_args()
