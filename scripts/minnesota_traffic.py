import requests


URL = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dot/trans_aadt_traffic_count_locs/shp_trans_aadt_traffic_count_locs.zip"
OUT_FILE = "data/traffic/minnesota_traffic.zip"


def main():
    r = requests.get(URL, stream=True)
    with open(OUT_FILE, 'wb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
    print(f"Wrote zipped traffic values to {OUT_FILE}")


if __name__ == "__main__":
    main()
