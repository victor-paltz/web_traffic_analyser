from LogGenerator import LogGenerator
from pprint import pprint as pp
import time
import os

from threading import Lock, Thread, Timer


def get_section_from_route(url):
    return url.split("/")[-1]


def compute_stats(logs):

    stats = {sec: {"nb_requests": 0,
                   "count_status": {"200": 0, "404": 0, "500": 0},
                   "count_methods": {"POST": 0, "GET": 0},
                   }
             for sec in sections}

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





sections = {"help", "user", "report"}
methods = {"GET", "POST"}
status = {200, 404, 500}

filename = "sample_csv.txt"

if __name__ == "__main__":

    lg = LogGenerator(filename, csv_start_date=None)
    delta_update = 2

    lg.start()

    while True:
        update_console(lg.empty_buffer())

        # faux, faire un delta
        time.sleep(delta_update)
