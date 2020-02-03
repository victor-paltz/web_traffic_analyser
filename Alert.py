from utils import format_time

class Alert:

    def __init__(self, start_time, hits, end_time=None):

        self.start_time = start_time
        self.hits = hits
        self.resolved = False

        if end_time is not None:
            self.resolved = True
            self.end_time = end_time
        

    def resolve(self, end_time):
        self.resolved = True
        self.end_time = end_time

    def report(self):
        report = ""
        report += f"- /!\ High traffic generated an alert - hits {self.hits:.2f} req/s, "
        report += f"triggered at time {format_time(self.start_time)}\n"
        if self.resolved:
            report += f"- End of alert, "
            report += f"recovered at time {format_time(self.end_time)}\n"
        else:
            report += "- Alert not recovered\n"

        return report
