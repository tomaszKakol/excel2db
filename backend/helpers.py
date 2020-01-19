import time
import datetime


def convert_date_to_timestamp(date):
    # tmp = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y")
    return datetime.timestamp(date)


def convert_timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)

def timestamp_now():
    return int(time.time())

