import tools
import config
import geojson
import pandas as pd
from sqlalchemy.sql import text


# get activities of all agents in given zones and time interval
# Return an array of dataframes for each zone
#
# Options:
# eg: startTime = '18:00:00' and endTime = '19:00:00'
# strictTime :  if true, only activities that start and end in the time interval are considered
#                   eg: an activity starting at 18:30:00 and ending at 19:00:00 is considered
#                       an activity starting at 18:30:00 and ending at 19:15:00 is NOT considered
#                       an activity starting at 17:00:00 and ending at 19:00:00 is NOT considered
#                       an activity starting starting or ending at null is NOT considered
#
#               if false, if an activity starts before the time interval or ends after the time interval, it is considered
#                   eg: an activity starting at 18:00:00 and ending at xx:xx:xx is considered
#                       an activity starting at 18:00:00 and ending at null is considered
#                       an activity starting at 17:00:00 and ending at 18:00:00 or later is considered
#                       an activity starting at 19:00:00 and ending at xx:xx:xx is NOT considered

def agentActivity(filePath, startTime='00:00:00', endTime='32:00:00', strictTime=False):
    conn = tools.connectToDatabase()
    allZonesDataframes = [] # list dataframes for all zones
    
    with open(filePath) as f:
        gjson = geojson.load(f)
        features = gjson["features"]
        nbFeatures = len(features)
        
        geojsonEpsg = tools.getEPSGFromGeoJSON(gjson)
        
        queryTemplate = f"""SELECT *, end_time - start_time as total_time_spent, 
                                CASE
                                    WHEN :startTime <= start_time and :endTime >= end_time then end_time - start_time
                                    WHEN :startTime >= start_time and :endTime >= end_time then end_time - :startTime
                                    WHEN :startTime > start_time and :endTime < end_time then TIME :endTime - TIME :startTime
                                    WHEN :startTime <= start_time and :endTime <= end_time then :endTime - start_time
                                    WHEN start_time is null and :endTime >= end_time then end_time - '18:00:00'
                                    WHEN start_time is null and :endTime < end_time then TIME'18:30:00' - TIME'18:00:00'
                                    WHEN :startTime > start_time and end_time is null then TIME'18:30:00' - TIME'18:00:00'
                                    WHEN :startTime <= start_time and end_time is null then '18:30:00' - start_time
                                    WHEN start_time is null and end_time is null then TIME'18:30:00' - TIME'18:00:00'
                                END as time_spent_in_interval
                            from activity 
                            where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                        """
        # Changing query depending on strictTime option
        if strictTime:
            query = text(queryTemplate + """and start_time between :startTime and :endTime
                                            and end_time between :startTime and :endTime""")
        else:
            query = text(queryTemplate + """and (start_time < :endTime or start_time is null)
                                            and (end_time > :startTime or end_time is null)""")
        
        for i in range(nbFeatures):
            currentFeature = features[i]
            currentGeometry = currentFeature["geometry"]
            currentCoordinates = currentGeometry["coordinates"]
            currentGeometryType = currentGeometry["type"]
            currentPolygon = tools.formatGeoJSONPolygonToPostgisPolygon(currentCoordinates, currentGeometryType, geojsonEpsg)
            
            query = query.bindparams(currentPolygon=currentPolygon, startTime=startTime, endTime=endTime)
            
            dataframe = pd.read_sql(query, conn)
            allZonesDataframes.append(dataframe)
    
    conn.close()
    
    return allZonesDataframes