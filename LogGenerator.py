import csv
import time
from threading import Lock, Thread

from Deserializer import Deserializer

filename = "sample_csv.txt"


class LogGenerator(Thread):

    def __init__(self, src_file, csv_start_date=None):
        Thread.__init__(self)

        # create a reader object on the input file.
        data = csv.reader(open(src_file), delimiter=',',
                          quoting=csv.QUOTE_NONNUMERIC)

        # store the header of the csv file.
        header = next(data)
        assert tuple(header) == ('remotehost', 'rfc931',
                                 'authuser', 'date', 'request', 'status', 'bytes')

        # Define Deserializers objects that transform any line of the csv into the right object.
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

        # Instanciate a generator that converts on the fly the csv lines into dictionary objects.
        self.stream = (log_deserializer(log_line) for log_line in data)

        # Instanciates Lock object to concurently access to variables.
        self.buffer_lock = Lock()
        self.run_lock = Lock()

        # Variable to handle the simulation.
        self.is_running = False
        self.csv_start_date = csv_start_date
        self.simul_start_time = time.time()

        # List that stores the lines already read.
        self.buffer = []

    def empty_buffer(self):
        """
        Function that empty the buffer and returns its content.

        Returns
        -------
        buffer : list of dict
            All the elements of the buffer (the requests that
            the machine received since the last flush of the buffer)
        """

        self.buffer_lock.acquire()
        buff = self.buffer.copy()
        self.buffer = []
        self.buffer_lock.release()
        return buff

    def get_buffer(self):
        """
        Function that returns the content of the buffer without flushing it.

        Returns
        -------
        buffer : list of dict
            All the elements of the buffer (the requests that
            the machine received since the last flush of the buffer)
        """

        self.buffer_lock.acquire()
        buff = self.buffer.copy()
        self.buffer_lock.release()
        return buff

    def stop(self):
        """
        Function to stop the Log generator.
        """

        self.run_lock.acquire()
        self.is_running = False
        self.run_lock.release()

    def get_offset_ms(self):
        """
        Function that returns the offset between the simulation start time and the csv-based time.

        Returns
        -------
        delta_time : int
            Number of seconds between the simulation start time and the csv-based time
        """
        
        return self.csv_start_date - self.simul_start_time

    def run(self):
        print("go")
        self.is_running = True

        if self.csv_start_date is not None:
            for log in self.stream:
                if log["date"] >= self.csv_start_date:
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

        self.simul_start_time = time.time()

        stop = False

        while not stop:

            for log in self.stream:

                self.run_lock.acquire()
                if not self.is_running:
                    self.run_lock.release()
                    stop = True
                    break
                self.run_lock.release()

                ellapsed_time = time.time() - self.simul_start_time
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
