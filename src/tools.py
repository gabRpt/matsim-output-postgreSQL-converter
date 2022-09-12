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



# converts a list of x lists to a string and replace Angle bracket with parenthesis
# [[[1, 2], [3,4], [5,6]]] -> "(((1,2) (3,4) (5,6)))"
def convertListToString(listToConvert):
    if isinstance(listToConvert, list):
        return " ".join(map(convertListToString, listToConvert)) + ")"
    else:
        return str(listToConvert)


# format geojson polygon to a postgis polygon
def formatGeoJSONPolygonToPostgisPolygon(coordinates, geometryType):
    polygon = convertListToString(coordinates)
    polygon = polygon.replace(") ", ", ")
    
    # limiting to 3 levels of nesting
    nbEndingParenthesis = polygon.count(")")
    if nbEndingParenthesis > 3:
        nbParenthesisToRemove = nbEndingParenthesis - 3
        polygon = polygon[:-nbParenthesisToRemove]
        nbEndingParenthesis = 3
    
    # adding nbEndingParenthesis parenthesis at the beggining
    polygon = "(" * nbEndingParenthesis + polygon
    polygon = geometryType + polygon
    
    return polygon