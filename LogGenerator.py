import csv
import time
from threading import Lock, Thread

import numpy as np

from .Deserializer import Deserializer

filename = "sample_csv.txt"


class LogGenerator(Thread):

    def __init__(self, src_file, csv_start_date=None):
        Thread.__init__(self)

        data = csv.reader(open(src_file), delimiter=',',
                          quoting=csv.QUOTE_NONNUMERIC)
        header = next(data)

        request_deserializer = Deserializer(deserialize_dict={"method": str,
                                                              "route": str,
                                                              "protocol": str},
                                            default_header=[
                                                "method", "route", "protocol"],
                                            split=True,
                                            default_sep=" ")

        transform_dict_log_line = {"authuser": str,
                                   "rfc931": str,
                                   "status": int,
                                   "remotehost": str,
                                   "request": request_deserializer,
                                   "bytes": int,
                                   "date": int
                                   }

        log_deserializer = Deserializer(deserialize_dict=transform_dict_log_line,
                                        default_header=header,
                                        split=False)

        self.stream = (log_deserializer(log_line) for log_line in data)

        self.generator_start_date = time.time()
        self.is_running = False

        self.buffer_lock = Lock()
        self.run_lock = Lock()

        self.csv_start_date = csv_start_date

        self.buffer = []
        print("ok")

    def pause(self):
        pass

    def empty_buffer(self):
        self.buffer_lock.acquire()
        buff = self.buffer.copy()
        self.buffer = []
        self.buffer_lock.release()
        return buff

    def get_buffer(self):
        self.buffer_lock.acquire()
        buff = self.buffer.copy()
        self.buffer_lock.release()
        return buff

    def stop(self):
        self.run_lock.acquire()
        self.is_running = False
        self.run_lock.release()

    def run(self):
        print("go")
        self.is_running = True

        if self.csv_start_date is not None:
            for log in self.stream:
                if log["date"] >= start_date:
                    self.buffer_lock.acquire()
                    self.buffer.append(log)
                    self.buffer_lock.release()
                    break
        else:
            for log in self.stream:
                self.csv_start_date = log["date"]
                self.buffer_lock.acquire()
                self.buffer.append(log)
                self.buffer_lock.release()
                break

        simul_start_time = time.time()

        stop = False

        while not stop:

            for log in self.stream:

                self.run_lock.acquire()
                if not self.is_running:
                    self.run_lock.release()
                    stop = True
                    break
                self.run_lock.release()

                ellapsed_time = time.time() - simul_start_time
                next_event = log["date"] - self.csv_start_date

                if ellapsed_time < next_event:
                    time.sleep(next_event-ellapsed_time)

                self.buffer_lock.acquire()
                self.buffer.append(log)
                self.buffer_lock.release()

        print("end")


if __name__ == "__main__":

    lg = LogGenerator(filename, csv_start_date=None)

    lg.start()

    time.sleep(3)

    print(len(lg.empty_buffer()))
    print(len(lg.empty_buffer()))

    time.sleep(1)

    print(len(lg.empty_buffer()))

    time.sleep(2)

    print(len(lg.empty_buffer()))
    print(len(lg.empty_buffer()))

    lg.stop()
