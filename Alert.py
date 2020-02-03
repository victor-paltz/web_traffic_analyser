from utils import format_time


class Alert:
    """
    Class that defines Alert objects
    """

    def __init__(self, start_time, hits, end_time=None):
        """
        Parameters
        ----------
        start_time : float
            Date when the alert was triggered in seconds
        hits : float
            Value of the average traffic that first exceeded the threshold
        end_time : float or None
            Date of the end of the alert in seconds (if the alert was resolved)
        """

        self.start_time = start_time
        self.hits = hits
        self.resolved = False

        if end_time is not None:
            self.resolved = True
            self.end_time = end_time

    def resolve(self, end_time):
        """
        Change the status of an alert from not resolved to resolved

        Parameters
        ----------
        end_time : float
            Date of the end of the alert in seconds 
        """

        self.resolved = True
        self.end_time = end_time

    def report(self):
        """
        generate a report on the alert
        """

        report = ""
        report += f"- /!\ High traffic generated an alert - hits {self.hits:.2f} req/s, "
        report += f"triggered at time {format_time(self.start_time)}\n"
        if self.resolved:
            report += f"      └─> End of alert, "
            report += f"recovered at time {format_time(self.end_time)}\n"
        else:
            report += "      └─> Alert not recovered\n"

        return report
