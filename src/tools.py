import config
from sqlalchemy import create_engine

def connectToDatabase():   
    engine = create_engine(config.DB_CONNECTION_STRING)
    conn = engine.connect()
    return conn

# correct time in hh:mm:ss format to reset 24 hours format
# eg if time is 25:12:30 it will return 01:12:30
# eg if time is 23:20:20 it will return 23:20:20
def checkAndCorrectTime(time):
    if time is not None and isinstance(time, str):
        if int(time[0:2]) > 23:
            time = str(int(time[0:2]) - 24) + time[2:]
    return time

# Returns the time in hh:mm:ss format
def getFormattedTime(timeInSeconds):
    if timeInSeconds is not None:
        if isinstance(timeInSeconds, float):
            timeInSeconds = int(timeInSeconds)
        m, s = divmod(timeInSeconds, 60)
        h, m = divmod(m, 60)
        return f'{h:d}:{m:02d}:{s:02d}'
    else:
        return None