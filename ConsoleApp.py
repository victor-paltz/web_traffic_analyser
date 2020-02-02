
import os
import time
from collections import deque
from threading import Lock, Thread
from analyser import compute_stats

from LogGenerator import LogGenerator


class ConsoleApp(Thread):

    def __init__(self, src_file, avg_trafic_threshold=10, refreshing_time=10):
        Thread.__init__(self)

        self.avg_trafic_threshold = avg_trafic_threshold
        self.refreshing_time = refreshing_time

        self.stream = LogGenerator(src_file, csv_start_date=1549573860)

        self.buffer = []

        self.total_traffic_120 = 0
        self.sliding_requests_number = deque([], 120)

        self.sections_stats_report = ""
        self.avg_total_traffic_report = ""
        self.alert_report = "List of alerts:\n"

        self.print_thread = Thread(target=self.print_reports)
        self.updater_thread = Thread(target=self.updater)

        self.alert = False
        self.alert_start_time = 0

    def run(self):
        self.print_thread.start()
        self.updater_thread.start()
        self.stream.start()

    def updater(self):

        last_total_requests_update = time.time()-1
        last_stats_update = time.time()-10

        nb_logs = 0

        while True:

            # get new logs
            new_logs = self.stream.empty_buffer()
            nb_logs += len(new_logs)
            #print(f"nb_log {nb_logs}")

            # store logs in buffer
            self.buffer.extend(new_logs)

            # trigger nb request update every 1s
            if time.time() - last_total_requests_update >= 1:

                #print(time.time() - last_total_requests_update)

                # update avg traffic value
                self.update_total_request(nb_logs)

                # reset nb_logs
                nb_logs = 0

                # mark the update date
                last_total_requests_update += 1

            # trigger stats computation every 10s
            if time.time() - last_stats_update >= 10:

                # update the sections' report
                self.update_sections_stats()

                # mark the update date
                last_stats_update += 10

            time.sleep(0.1)

    def print_reports(self):
        while True:

            total_update = f" (last update: {format_time(time.time()+self.stream.get_offset_ms())})"

            report = f"HTTP log monitoring console program {total_update}\n\n"
            report += self.sections_stats_report
            report += "\n"
            report += self.avg_total_traffic_report
            report += "\n"
            report += self.alert_report
            report += "\n"

            os.system('clear')
            print(report)

            time.sleep(0.5)

    def update_total_request(self, nb_logs):

        if len(self.sliding_requests_number) == 120:
            self.total_traffic_120 -= self.sliding_requests_number.popleft()
        self.sliding_requests_number.append(nb_logs)
        self.total_traffic_120 += nb_logs

        avg_total_traffic = self.total_traffic_120/120

        report = f"Average total taffic: {avg_total_traffic:.2f} req/s over 2min-sliding window"
        if True:
            report += f" (last update: {format_time(time.time()+self.stream.get_offset_ms())})"

        report += "\n"
        self.avg_total_traffic_report = report

        if self.alert:
            if avg_total_traffic < self.avg_trafic_threshold:
                self.alert = False
                self.alert_report += f"End of alert"
                self.alert_report += f", recovered at time {format_time(time.time()+self.stream.get_offset_ms())}\n"
        else:
            if avg_total_traffic >= self.avg_trafic_threshold:
                self.alert = True
                self.alert_report += f"/!\ High traffic generated an alert - hits {avg_total_traffic:.2f} req/s, "
                self.alert_report += f"triggered at time {format_time(time.time()+self.stream.get_offset_ms())}\n"

    def update_sections_stats(self, verbose=False):

        total, stats = compute_stats(self.buffer)

        self.buffer = []

        infos = sorted(((stats[st]["nb_requests"], st, stats[st])
                        for st in stats), reverse=True)

        report = f"Top {3} websites:"
        if True:
            report += f" (last update: {format_time(time.time()+self.stream.get_offset_ms())})"

        report += "\n"

        nb_requests = 0

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

        self.sections_stats_report = report


def format_time(nb_sec):
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(nb_sec))
    return f"{time_string}.{int((nb_sec-int(nb_sec))*100):02d}"


if __name__ == "__main__":

    app = ConsoleApp("sample_csv.txt")
    app.start()
