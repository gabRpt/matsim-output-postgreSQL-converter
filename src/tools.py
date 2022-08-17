import config
from sqlalchemy import create_engine

def connectToDatabase():   
    engine = create_engine(config.DB_CONNECTION_STRING)
    conn = engine.connect()
    return conn

# Converts hh:mm:ss time to x days x hours x minutes x seconds
def formatTimeToIntervalType(time):
    if time is not None and isinstance(time, str):
        time = time.split(':')
        formattedTime = ""
        if int(time[0]) > 23:
            formattedTime += str(int(time[0]) // 24) + " days "
            time[0] = int(time[0]) % 24
        
        formattedTime += f'{time[0]} hours {time[1]} minutes {time[2]} seconds'
        return formattedTime
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