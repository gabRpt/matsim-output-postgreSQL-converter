import tools
import geojson
import re
from sqlalchemy.sql import text



def matrixOD(filePath):
    conn = tools.connectToDatabase()
    
    with open(filePath) as f:
        gjson = geojson.load(f)
        features = gjson["features"]

        # init OD matrix
        nbFeatures = len(features)
        finalODMatrix = [[0 for x in range(nbFeatures)] for y in range(nbFeatures)]
                
        for i in range(nbFeatures):
            startingFeature = features[i]
            startingGeometry = startingFeature["geometry"]
            startingCoordinates = startingGeometry["coordinates"]
            startingGeometryType = startingGeometry["type"]
            startingPolygon = formatPolygon(startingCoordinates, startingGeometryType)

            # creating OD matrix of count of trips between each points
            for j in range(nbFeatures):
                endingFeature = features[j]
                endingGeometry = endingFeature["geometry"]
                endingCoordinates = endingGeometry["coordinates"]
                endingGeometryType = endingGeometry["type"]

                endingPolygon = formatPolygon(endingCoordinates, endingGeometryType)                    
                
                query = text("""SELECT count(*)
                                from trip
                                where trip.id IN (SELECT t.id
                                        from facility f
                                        join trip t ON t.start_facility_id = f.id
                                        where ST_Contains(ST_GeomFromText(:startingPolygon), "location"))
                                AND trip.id IN  (SELECT t.id
                                        from facility f
                                        join trip t ON t.end_facility_id = f.id
                                        where ST_Contains(ST_GeomFromText(:endingPolygon), "location"))
                            """)
                query = query.bindparams(startingPolygon=startingPolygon, endingPolygon=endingPolygon)

                result = conn.execute(query)
                
                finalODMatrix[i][j] = result.fetchone()[0]                        

    print(finalODMatrix)
    conn.close()


# converts a list of x lists to a string and replace Angle bracket with parenthesis
# [[[1, 2], [3,4], [5,6]]] -> "(((1,2) (3,4) (5,6)))"
def convertListToString(listToConvert):
    if isinstance(listToConvert, list):
        return " ".join(map(convertListToString, listToConvert)) + ")"
    else:
        return str(listToConvert)

def formatPolygon(coordinates, geometryType):
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