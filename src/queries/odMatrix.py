import tools
import config
import geojson
import pandas as pd
from pyproj import Proj, transform
from sqlalchemy.sql import text
from shapely import wkt


# get OD Matrix of all agents between given zones and time interval
#
# Options:
# eg: startTime = '18:00:00' and endTime = '19:00:00'
# ignoreArrivalTime : if true, only startTime is considered
#   eg: a trip having dep_time = 18:00:00 and trav_time = 00:30:00 is considered
#       a trip having dep_time = 18:00:00 and trav_time = 01:30:00 is NOT considered (arrivalTime = 19:30:00 is not in interval)
# if False:
#   eg : a trip having dep_time = 18:00:00 and trav_time = 00:30:00 is considered
#        a trip having dep_time = 18:00:00 and trav_time = 01:30:00 is considered
# in both cases, if a trip has a dep_time < 18:00:00 it will not be considered
def odMatrix(filePath, startTime='00:00:00', endTime='23:59:59', ignoreArrivalTime=True, generateArabesqueFiles=False):
    conn = tools.connectToDatabase()
    
    with open(filePath) as f:
        gjson = geojson.load(f)
        features = gjson["features"]
        
        gjsonEpsg = _getEPSGFromGeoJSON(gjson)
        # print(f"GeoJSON EPSG : {gjsonEpsg}")

        # init OD matrix
        nbFeatures = len(features)
        finalODMatrix = [[-1 for x in range(nbFeatures)] for y in range(nbFeatures)]
        
        zonesCentroids = []
        
        # Setting up the query
        query = f"""SELECT count(*)
                    from trip
                    where trip.id IN (SELECT t.id
                            from facility f
                            join trip t ON t.start_facility_id = f.id
                            where ST_Contains(ST_Transform(ST_GeomFromText(:startingPolygon, {gjsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID})))
                    AND trip.id IN  (SELECT t.id
                            from facility f
                            join trip t ON t.end_facility_id = f.id
                            where ST_Contains(ST_Transform(ST_GeomFromText(:endingPolygon, {gjsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID})))
                    AND dep_time < :endTime
                """
        
        if not ignoreArrivalTime:
            query += """ and (dep_time + trav_time) > :startTime
                        and (dep_time + trav_time) < :endTime """
        
        query = text(query)
                
        for i in range(nbFeatures):
            startingFeature = features[i]
            startingGeometry = startingFeature["geometry"]
            startingCoordinates = startingGeometry["coordinates"]
            startingGeometryType = startingGeometry["type"]
            startingPolygon = tools.formatGeoJSONPolygonToPostgisPolygon(startingCoordinates, startingGeometryType, gjsonEpsg)

            # Adding coordinates of the centroid of the zone
            zonesCentroids.append(wkt.loads(startingPolygon).centroid)
            
            
            # creating OD matrix of count of trips between each points
            for j in range(nbFeatures):
                endingFeature = features[j]
                endingGeometry = endingFeature["geometry"]
                endingCoordinates = endingGeometry["coordinates"]
                endingGeometryType = endingGeometry["type"]

                endingPolygon = tools.formatGeoJSONPolygonToPostgisPolygon(endingCoordinates, endingGeometryType, gjsonEpsg)                    
                
                if ignoreArrivalTime:
                    query = query.bindparams(startingPolygon=startingPolygon, endingPolygon=endingPolygon, endTime=endTime)
                else:
                    query = query.bindparams(startingPolygon=startingPolygon, endingPolygon=endingPolygon, startTime=startTime, endTime=endTime)

                result = conn.execute(query)
                
                finalODMatrix[i][j] = result.fetchone()[0]

    for i in finalODMatrix:
        print('\t'.join(map(str, i)))
 
    conn.close()
    
    if generateArabesqueFiles:
        gjsonEpsg = f'epsg:{gjsonEpsg}'
        locationDf, flowDf = _getArabesqueDataframesFromODMatrix(finalODMatrix, zonesCentroids, gjsonEpsg)
        _generateArabesqueFiles('./generated/', locationDf, flowDf)
    
    return finalODMatrix

# return two dataframes from the odMatrix
# locationDf : contains the centroids of the zones with their latitudes and longitudes
# flowDf : contains the flows between each zones
def _getArabesqueDataframesFromODMatrix(odMatrix, zonesCentroids, geojsonEpsg):
    locationDict = {
        "id": [],
        "lat": [],
        "lng": []
    }
    
    flowDict = {
        "origin": [],
        "destination": [],
        "value": []
    }
    
    nbZones = len(zonesCentroids)
    
    # config for the transformation of the coordinates
    outEpsg = f'epsg:{config.DEFAULT_ARABESQUE_SRID}'
    inProj = Proj(geojsonEpsg)
    outProj = Proj(outEpsg)
    
    for startZone in range(nbZones):
        locationDict["id"].append(startZone)
        
        # transform the coordinates
        if geojsonEpsg != outEpsg:
            x1, y1 = zonesCentroids[startZone].x, zonesCentroids[startZone].y
            x2, y2 = transform(inProj, outProj, x1, y1)
            locationDict["lat"].append(x2)
            locationDict["lng"].append(y2)
        else:
            locationDict["lat"].append(zonesCentroids[startZone].x)
            locationDict["lng"].append(zonesCentroids[startZone].y)
        
        for endZone in range(nbZones):
            if odMatrix[startZone][endZone] > 0:
                flowDict["origin"].append(startZone)
                flowDict["destination"].append(endZone)
                flowDict["value"].append(odMatrix[startZone][endZone])
    
    locationDf = pd.DataFrame(locationDict)
    flowDf = pd.DataFrame(flowDict)
    
    return locationDf, flowDf


def _generateArabesqueFiles(filePath, locationDf, flowDf):
    locationDf.to_csv(filePath + "location.csv", index=False)
    flowDf.to_csv(filePath + "flow.csv", index=False)
    
    return 1


# Return the EPSG of the geojson
# if not found return the Arabesque default EPSG
def _getEPSGFromGeoJSON(gjson):
    epsg = None

    try:
        crs = gjson['crs']['properties']['name']
        
        # get the EPSG code
        for i in crs.split(':'):
            if i.isdigit():
                epsg = int(i)
                break
        
        if epsg is None:
            raise Exception("No EPSG code found in the GeoJSON file")

    except:
        print("No EPSG code found in the GeoJSON file")
        epsg = config.DEFAULT_ARABESQUE_SRID

    return epsg