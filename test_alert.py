

from ConsoleApp import ConsoleApp
from LogGenerator import LogGenerator


def create_test_csv(path):
    first_part = '"10.0.0.2","-","apache",'
    second_part = ',"GET /api/user HTTP/1.0",200,1234\n'

    with open(path, "w") as f:
        f.writelines(
            '"remotehost","rfc931","authuser","date","request","status","bytes"\n')

        for i in range(20, 80):
            s = first_part+str(i)+second_part
            f.writelines(s for _ in range(20))


def test_alert():
    test_path = "data/test_csv.txt"

    create_test_csv(test_path)

    console_app = ConsoleApp(test_path, avg_trafic_threshold=10, csv_start_date=0)

    console_app.start()

    time.sleep(90)

    assert len(console_app.alert_list) == 1
    assert not console_app.alert_list[0].resolved
    assert abs(console_app.alert_list[0].start_time - 80) <= 1

    time.sleep(40)

    assert len(console_app.alert_list) == 1
    assert console_app.alert_list[0].resolved
    assert abs(console_app.alert_list[0].end_time - 120) <= 1

    console_app.stop()
    console_app.join()


if __name__ == "__main__":
    test_alert()
