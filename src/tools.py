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
def formatGeoJSONPolygonToPostgisPolygon(coordinates, geometryType, epsg):
    # print(coordinates)
    # coordinates = convertCoordinatesToDatabaseCRS(coordinates, epsg)
    polygon = convertListToString(coordinates)
    polygon = polygon.replace(") ", ", ")
    
    # Removing 1 level of parenthesis
    # (((1,2) (3,4) (5,6))) -> ((1,2) (3,4) (5,6))
    # this caused an error while creating the geometry
    nbEndingParenthesis = polygon.count(")")
    polygon = polygon[:-1]
    nbEndingParenthesis -= 1
    
    # adding nbEndingParenthesis parenthesis at the beginning
    polygon = "(" * nbEndingParenthesis + polygon    
    polygon = geometryType + polygon
    
    print(polygon)
    # quit()
    return polygon

def convertCoordinatesToDatabaseCRS(coordinates, epsg):    
    getNestingLevel = lambda l: isinstance(l, list) and max(map(getNestingLevel, l))+1
    nestingLevel = getNestingLevel(coordinates)
    
    if nestingLevel == 3:
        for i in range(len(coordinates)):
            for j in range(len(coordinates[i])):
                print(coordinates[i][j])
                coordinates[i][j] = f"ST_Transform(ST_SetSRID(ST_MakePoint({coordinates[i][j][0]}, {coordinates[i][j][1]}), {epsg}), {config.DB_SRID})"
                print(coordinates[i][j])
    
    return coordinates