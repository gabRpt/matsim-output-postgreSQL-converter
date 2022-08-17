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

# Convert seconds to x days x hours x minutes x seconds
def formatTimeToIntervalType(time):
    if time is not None:
        if isinstance(time, float):
            time = int(time)
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return f'{d} days {h} hours {m} minutes {s} seconds'
    else:
        return None
            

# Returns the time in hh:mm:ss format
def getFormattedTime(timeInSeconds):
    if timeInSeconds is not None:
        if isinstance(timeInSeconds, float):
            timeInSeconds = int(timeInSeconds)
        m, s = divmod(timeInSeconds, 60)
        h, m = divmod(m, 60)
        if h < 10:
            h = '0' + str(h)
        else:
            h = str(h)
        return f'{h}:{m:02d}:{s:02d}'
    else:
        return None