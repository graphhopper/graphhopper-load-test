import json
import os
import random

from locust import events


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
    headers = {"content-type": "application/json"}
    with task_set.client.post(url, catch_response=True, headers=headers, name="Info", timeout=3) as response:
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


def setup_locust_debugging():
    if "DEBUG" in os.environ and os.environ["DEBUG"] == "yes":
        def report_error(request_type, name, response_time, exception, **kwargs):
            print(f"Request {name} ({request_type}) failed: {exception}", flush=True)
        events.request_failure.add_listener(report_error)
