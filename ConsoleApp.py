
import os
import time
from collections import deque
from threading import Lock, Thread

from Alert import Alert
from log_analyse_fcts import compute_stats
from LogGenerator import LogGenerator
from utils import format_time


class ConsoleApp:
    """
    Class that describes a console application for our project.
    """

    def __init__(self, src_file, avg_trafic_threshold=10, csv_start_date=1549573860):
        """
        Parameters
        ----------
        src_file : string
            Path to the csv file containing the logs.
        avg_trafic_threshold : int 
            Average traffic threshold to trigger alerts (in requests per second).
            If the average traffic on a slidding window of 2 minutes is above this
            threshold, an alert is triggered.
        """

        # Threshold on the average traffic
        self.avg_trafic_threshold = avg_trafic_threshold

        # Log generator object
        self.stream = LogGenerator(src_file, csv_start_date=csv_start_date)

        # buffer that contains the logs not already processed
        self.buffer = []

        # variable that stores the total number of requests
        # on a sliding window of 2 minutes.
        self.total_traffic_120 = 0
        # we store the number of requests of each second in a fixed sized queue.
        self.sliding_requests_number = deque([], 120)

        # Variable that contains the reports to show on the console
        self.sections_stats_report = ""
        self.avg_total_traffic_report = ""
        self.alert_report = ""

        # We define a thread to update the screen of the console app
        self.print_thread = Thread(target=self.print_reports)
        self.run_printing = True

        # We define a thread to retrive the new logs and process them
        self.updater_thread = Thread(target=self.updater)
        self.run_updater = True

        # Variables for alerts
        self.alert = False
        self.alert_start_time = 0
        self.alert_list = []

    def start(self):
        """
        Function to start all the threads
        """

        self.print_thread.start()
        self.updater_thread.start()
        self.stream.start()

    def stop(self):
        """
        Function to stop the simulation
        """

        self.stream.stop()
        self.run_printing = False
        self.run_updater = False
        self.print_thread.join()
        self.updater_thread.join()
        self.stream.join()

    def updater(self):
        """
        Function that triggers update events in the right time
        and retrieves logs from buffer.
        """

        stats_period = 10  # seconds
        request_period = 1  # second

        next_total_requests_update = time.time()-request_period
        next_stats_update = time.time()-stats_period

        nb_logs = 0

        while self.run_updater:

            # get new logs
            new_logs = self.stream.empty_buffer()
            nb_logs += len(new_logs)

            # store logs in buffer
            self.buffer.extend(new_logs)

            # trigger nb request update every 1s
            if time.time() - next_total_requests_update >= request_period:

                # update avg traffic value
                self.update_total_request_report(nb_logs)

                # reset nb_logs
                nb_logs = 0

                # mark the update date
                next_total_requests_update += request_period

            # trigger stats computation every 10s
            if time.time() - next_stats_update >= stats_period:

                # update the sections' report
                self.update_sections_stats_report()

                # mark the update date
                next_stats_update += stats_period

            time.sleep(0.1)

    def print_reports(self):
        """
        Function that updates the console with the reports every 0.5 seconds
        """

        self.update_alert_report()

        while self.run_printing:

            # prepare report
            total_update = f" (last update: {format_time(time.time()+self.stream.get_offset_ms())})"
            report = f"HTTP log monitoring console program {total_update}\n\n"
            report += self.sections_stats_report
            report += "\n"
            report += self.avg_total_traffic_report
            report += "\n"
            report += self.alert_report

            # print report
            os.system('clear')
            print(report)

            # wait some time
            time.sleep(0.5)

    def update_total_request_report(self, nb_logs):
        """
        Function that computes the report for the average total traffic.
        The function manage also alerts if any.

        Parameters
        ----------
        nb_logs : int
            number of new logs that appeared since last update
        """

        # update the total traffic using a fixed size queue
        if len(self.sliding_requests_number) == 120:
            self.total_traffic_120 -= self.sliding_requests_number.popleft()
        self.sliding_requests_number.append(nb_logs)
        self.total_traffic_120 += nb_logs

        # compute the average traffic
        avg_total_traffic = self.total_traffic_120/120

        # create report and update traffic report
        report = f"Average total taffic: {avg_total_traffic:.2f} req/s over 2min-sliding window"
        if True:
            report += f" (last update: {format_time(time.time()+self.stream.get_offset_ms())})"
        report += "\n"
        self.avg_total_traffic_report = report

        # Handle alerts
        if self.alert:
            # resolve alert if the condition is satisfied
            if avg_total_traffic < self.avg_trafic_threshold:
                self.alert = False
                alert_time = time.time() + self.stream.get_offset_ms()
                self.alert_list[-1].resolve(alert_time)
                self.update_alert_report()
        else:
            # trigger and alert if the threshold was exceeded
            if avg_total_traffic >= self.avg_trafic_threshold:
                self.alert = True
                alert_time = time.time() + self.stream.get_offset_ms()
                self.alert_list.append(Alert(alert_time, avg_total_traffic))
                self.update_alert_report()

    def update_sections_stats_report(self, verbose=False):
        """
        Function that updates the report that deals with statistics
        every 10 seconds and about each sections.

        Parameters
        ----------
        verbose : bool
            Define the level of detail of the stats, default to False (low level of details)
        """

        # compute stats
        total, stats = compute_stats(self.buffer)

        self.buffer = []

        # sort sections by number of requests
        infos = sorted(((stats[st]["nb_requests"], st, stats[st])
                        for st in stats), reverse=True)

        # create a report
        report = f"Top {3} websites:"
        if True:
            report += f" (last update: {format_time(time.time()+self.stream.get_offset_ms())})"
        report += "\n"

        nb_requests = 0

        # for each section, format stats and append it to the report
        for i, (count_req, section, section_stats) in enumerate(infos):

            nb_requests = section_stats["nb_requests"]
            ratio_requests = nb_requests/total if total else 0
            nb_post = section_stats["count_methods"]["POST"]
            nb_get = section_stats["count_methods"]["GET"]
            nb_404 = section_stats["count_status"]["404"]
            nb_500 = section_stats["count_status"]["500"]

            report += f"{i+1}: Section {section}: \t traffic: {100*ratio_requests:.1f}%"
            report += f", requests: {nb_requests}"
            if verbose:
                report += f" (GET:{nb_get}, POST:{nb_post})"
                report += f", errors: {nb_404+nb_500} (404: {nb_404}, 500: {nb_500})"
            report += "\n"

        # finally update the section report
        self.sections_stats_report = report

    def update_alert_report(self):
        """
        Function that update the alert report
        """

        # custom report if no alert ever triggered
        if not self.alert_list:
            self.alert_report = "No alert triggered"
            return

        # create the report
        report = "List of alerts:\n"

        # add a description line for each alert
        for alert in self.alert_list:
            report += alert.report()

        # finally update the alert report
        self.alert_report = report


if __name__ == "__main__":

    app = ConsoleApp("data/sample_csv.txt", csv_start_date=0)
    app.start()

    time.sleep(10)

    app.stop()
