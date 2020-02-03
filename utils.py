import time

def format_time(nb_sec):
    """
    Function to format a number of seconds into a string

    Parameters
    ----------
    nb_sec : float
        Number of seconds.

    Returns
    -------
    output : string
        formated time with millisecond precision
    """

    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(nb_sec))
    return f"{time_string}.{int((nb_sec-int(nb_sec))*100):02d}"