import requests

from constants import TRAFFIC_ZIP_PATH, TRAFFIC_URL
from logs import log


def main():
    r = requests.get(TRAFFIC_URL, stream=True)
    with open(TRAFFIC_ZIP_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
    log(f"Wrote zipped traffic values to {TRAFFIC_ZIP_PATH}")


if __name__ == "__main__":
    main()
