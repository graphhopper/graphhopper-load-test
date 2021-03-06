import json
import os
import random
import requests


def get_api_key_url_suffix(prefix):
    """Return something like `?key=1234567890` or empty if no key set"""
    if "API_KEY" not in os.environ:
        return ""
    return f"{prefix}key={os.environ['API_KEY']}"


def get_random_berlin_point():
    """For the GraphHopper Berlin area."""
    return [
        random.uniform(52.522906, 52.561958),
        random.uniform(13.347702, 13.437996)
    ]


def get_points_query(task_set):
    """Generate or load the points query parameters."""

    # the query possibly hardcoded in environment?
    if "QUERY_POINTS" in os.environ:
        return os.environ["QUERY_POINTS"]

    # get the bounding box from the /info
    info_uri = "/info"
    api_key_url_suffix = get_api_key_url_suffix("?")
    url = f"{info_uri}{api_key_url_suffix}"
    full_url = f"{task_set.user.host}{url}"
    headers = {"content-type": "application/json"}
    try:
        response = requests.get(full_url, headers=headers, timeout=3)
    except:
        raise Exception(f"Can't get info from {full_url}.")
    if response.text is None:
        response.failure("Info failed: no response from the info endpoint.")
        return
    try:
        data = response.json()
    except json.decoder.JSONDecodeError as e:
        response.failure("Info failed: {}".format(e))
        return
    if "bbox" not in data:
        response.failure(f"No bounding box in info: {data}")
        return

    # get a point in the middle of the bounding box (if not at (0, 0))
    lon1, lat1, lon2, lat2 = data["bbox"]
    lon, lat = [(lon2 + lon1) / 2, (lat2 + lat1) / 2]
    if lon < 1.0 and lon > -1.0:  # make sure we don't strike at 0.0
        lon, lat = max(lon1, lon2) / 2, max(lat1, lat2) / 2

    num_points = 3 if "QUERY_POINTS_NUM" not in os.environ else int(os.environ["QUERY_POINTS_NUM"])
    return "&".join([f"point={lat},{lon}" for _ in range(num_points)])
