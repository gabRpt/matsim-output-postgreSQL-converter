import tools
import config
import geojson
import pandas as pd
from sqlalchemy.sql import text
from datetime import datetime


# TODO change default interval to 15 minutes
# Return the activity sequences for a every users during a given timespan (by default, 00:00:00 to 32:00:00) 
# with the given interval (by default, 60 minutes)
# in the given zone (geojson file)

def activitySequences(filePath, startTime='00:00:00', endTime='32:00:00', interval=60):
    agentProcessTimer = datetime.now() # timer to measure the time it takes to process all agents
    nbAgentsProcessed = 0
    
    
    conn = tools.connectToDatabase()
    
    startTimeInSeconds = tools.getTimeInSeconds(startTime)
    endTimeInSeconds = tools.getTimeInSeconds(endTime)
    intervalInSeconds = interval * 60
    
    with open(filePath) as f:
        gjson = geojson.load(f)
        features = gjson["features"]
        nbFeatures = len(features)
        
        geojsonEpsg = tools.getEPSGFromGeoJSON(gjson)
        
        queryTemplate = None
        
        currentFeature = features[0]
        currentGeometry = currentFeature["geometry"]
        currentCoordinates = currentGeometry["coordinates"]
        currentGeometryType = currentGeometry["type"]
        currentPolygon = tools.formatGeoJSONPolygonToPostgisPolygon(currentCoordinates, currentGeometryType, geojsonEpsg)
        
        queryAllAgentsInZone = text(f"""SELECT distinct "personId"
                                        from activity
                                        where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                                    """)
        
        print("Getting all agents in zone...")
        queryAllAgentsInZone = queryAllAgentsInZone.bindparams(currentPolygon=currentPolygon)
        allAgentsInZoneDf = pd.read_sql(queryAllAgentsInZone, conn)
        
        
        # get all activities of all agents in the zone during the given timespan
        print("Getting all activities of all agents in the zone during the given timespan...")
        activityDfList = []
        while startTimeInSeconds < endTimeInSeconds:
            currentEndTimeInSeconds = startTimeInSeconds + intervalInSeconds
            currentStartTimeFormatted = tools.getFormattedTime(startTimeInSeconds)
            currentEndTimeFormatted = tools.getFormattedTime(currentEndTimeInSeconds)
                            
            query = text(f"""SELECT *
                            from activity 
                            where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                            and (start_time between :currentStartTimeFormatted and :currentEndTimeFormatted or start_time is null)
                            and (end_time between :currentStartTimeFormatted and :currentEndTimeFormatted or end_time is null)
                        """)
            query = query.bindparams(currentPolygon=currentPolygon, 
                                        currentStartTimeFormatted=currentStartTimeFormatted, 
                                        currentEndTimeFormatted=currentEndTimeFormatted)
            
            dataframe = pd.read_sql(query, conn)
            activityDfList.append(dataframe)
            
            # add interval to startTime
            startTimeInSeconds += intervalInSeconds
            
        
        
        print("Merging all activities of all agents in the zone during the given timespan...")
        # take the first 200 agents
        allAgentsInZone = allAgentsInZoneDf["personId"].tolist()
        allAgentsInZone = allAgentsInZone[:200]
        
        for currentAgent in allAgentsInZone:
            startTimeInSeconds = tools.getTimeInSeconds(startTime)
            endTimeInSeconds = tools.getTimeInSeconds(endTime)
            currentActivityDfIndex = 0
            
            while startTimeInSeconds < endTimeInSeconds:
                currentEndTimeInSeconds = startTimeInSeconds + intervalInSeconds
                currentStartTimeFormatted = tools.getFormattedTime(startTimeInSeconds)
                currentEndTimeFormatted = tools.getFormattedTime(currentEndTimeInSeconds)
                
                # get all activities of the current agent during the current interval
                currentActivityDf = activityDfList[currentActivityDfIndex]
                concernedAgentActivityDf = currentActivityDf[currentActivityDf["personId"] == currentAgent]
                
                currentActivityDfIndex += 1
                startTimeInSeconds += intervalInSeconds
            
            nbAgentsProcessed += 1
        
        print(f"Processed {nbAgentsProcessed} agents in {datetime.now() - agentProcessTimer}")
                
    
    return 1