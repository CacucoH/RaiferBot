DIRECTORY = "/tmp/raifa_bot/logs/"
DAYS_AMOUNT = 2

from datetime import datetime, timedelta
import os


def iterate(pattern: datetime):
    for i in os.listdir():
        str_date = i[4:-10]
        file_date = datetime.strptime(str_date, "%Y-%m-%d")

        if file_date <= pattern:
            try:
                os.remove(i)
            except:
                continue
        

def start():
    os.chdir(DIRECTORY)
    old_files = datetime.now() - timedelta(days=DAYS_AMOUNT)
    iterate(old_files)

start()