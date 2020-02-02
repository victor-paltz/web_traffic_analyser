import os
import time
from pprint import pprint as pp
from threading import Lock, Thread, Timer

from LogGenerator import LogGenerator


SECTIONS = {"help", "user", "report"}
METHODS = {"GET", "POST"}
STATUS = {200, 404, 500}


def get_section_from_route(url):
    """
    extract the section from an url or a route.

    Parameters
    ----------
    url : string
        url or route

    Returns
    -------
    section : string
        section accessed by the url/route
    """
    return url.split("/")[-1]


def compute_stats(logs):
    """
    Compute stats over a list of logs.

    Parameters
    ----------
    logs : list of dict
        list of log objects

    Returns
    -------
    total : int
        The total number of requests in the log list (=len(logs))
    stats: dict
        A dictionary gathering some statistics about the given logs.
    """

    stats = {sec: {"nb_requests": 0,
                   "count_status": {"200": 0, "404": 0, "500": 0},
                   "count_methods": {"POST": 0, "GET": 0},
                   }
             for sec in SECTIONS}

    total = 0

    for log in logs:

        total += 1

        section = get_section_from_route(log["request"]["route"])
        method = log["request"]["method"]
        status = log["status"]

        stats[section]["count_status"][str(status)] += 1
        stats[section]["nb_requests"] += 1
        stats[section]["count_methods"][method] += 1

    return total, stats


if __name__ == "__main__":

    filename = "sample_csv.txt"
    lg = LogGenerator(filename, csv_start_date=None)
    delta_update = 2

    lg.start()

    while True:
        update_console(lg.empty_buffer())

        # faux, faire un delta
        time.sleep(delta_update)
