import tools
import geojson
import tools
from sqlalchemy.sql import text



def odMatrix(filePath):
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
            startingPolygon = tools.formatGeoJSONPolygonToPostgisPolygon(startingCoordinates, startingGeometryType)

            # creating OD matrix of count of trips between each points
            for j in range(nbFeatures):
                endingFeature = features[j]
                endingGeometry = endingFeature["geometry"]
                endingCoordinates = endingGeometry["coordinates"]
                endingGeometryType = endingGeometry["type"]

                endingPolygon = tools.formatGeoJSONPolygonToPostgisPolygon(endingCoordinates, endingGeometryType)                    
                
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