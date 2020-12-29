"""
Run Locust programmatically.
"""

import gevent

import main
from utils import color

from locust.env import Environment
from locust.stats import stats_history
from locust.util.timespan import parse_timespan


def run(settings):
    """
    Run the load test programmatically.
    """
    env = Environment(
        user_classes=[getattr(main, settings["persona_arg"])],
        host=settings["base_url"],
    )
    env.create_local_runner()

    # start a greenlet that saves current stats to history
    gevent.spawn(stats_history, env.runner)

    # start the load test
    env.runner.start(
            user_count=int(settings["users"]),
            spawn_rate=int(settings["users"]))

    # add a listener for failures
    env.events.request_failure.add_listener(main.failure_handler)

    # stop the runner at the end
    duration_s = parse_timespan(settings["duration"])
    gevent.spawn_later(duration_s, lambda: stop(env))

    # wait for the greenlets
    env.runner.greenlet.join()


def parse_locust_stats(env):
    """
    Turn the locust stats into more print-friendly data.
    """
    stats = env.runner.stats
    statistics = {
        "requests": {},
        "failures": {},
        "num_requests": stats.num_requests,
        "num_requests_fail": stats.num_failures,
    }

    for name, value in stats.entries.items():
        locust_task_name = "{0}_{1}".format(name[1], name[0])
        statistics["requests"][locust_task_name] = {
            "num_requests": value.num_requests,
            "min_response_time": value.min_response_time,
            "median_response_time": value.median_response_time,
            "avg_response_time": value.avg_response_time,
            "max_response_time": value.max_response_time,
            "total_rps": value.total_rps,
        }

    for id, error in env.runner.errors.items():
        error_dict = error.to_dict()
        locust_task_name = "{0}_{1}".format(
            error_dict["method"], error_dict["name"]
        )
        statistics["failures"][locust_task_name] = error_dict

    return statistics


def stop(env):
    """
    Stop the running load test.
    """
    env.runner.quit()
    stats = parse_locust_stats(env)
    print_results(stats)


def print_results(data):
    """
    Print the end results of the load test.
    """
    print("")
    print(
        f"{'Name':<30} {'# reqs':>7} {'# fails':>12} {'Avg':>7} {'Min':>7} "
        f"{'Max':>7}  | {'Median':>7} {'req/s':>7}"
    )
    print("-" * 94)
    for name, page in data["requests"].items():
        for c in [
            "min_response_time",
            "max_response_time",
            "avg_response_time",
            "median_response_time",
        ]:
            page[c] = (
                f"{float(page[c]):>7.0f}" if page[c] is not None else f"{'N/A':>7}"
            )
        nice_name = name.replace("_", " ")
        num_fails = (
            0 if name not in data["failures"] else data["failures"][name]["occurrences"]
        )
        print(
            f"{nice_name:<30} {page['num_requests']:>7} {num_fails:>12} "
            f"{page['avg_response_time']} {page['min_response_time']} "
            f"{page['max_response_time']}  | {page['median_response_time']} "
            f"{page['total_rps']:>7.2f}"
        )
    print("-" * 94)
    pages = data["requests"].values()
    total_num_requests = sum(page["num_requests"] for page in pages)
    total_num_failures = sum(f["occurrences"] for f in data["failures"].values())
    total_rps = sum(page["total_rps"] for page in pages)
    print(
        f"{'Total':<30} {total_num_requests:>7} {total_num_failures:>12} "
        f"{' ':>34} {total_rps:>7.2f}"
    )

    # Errors
    print("")
    errors = sorted(data["failures"].values(), key=lambda x: -x["occurrences"])
    if not errors:
        print(color.green_bg("No errors!"))
    else:
        print(color.red_bg("Error report:"))
        print("# occurrences  Error")
        print("-" * 140)
        for error in errors:
            msg = f"{error['method']} {error['name']}: {error['error']}"
            print(f"{error['occurrences']:>13}  {msg}")
        print("-" * 140)
