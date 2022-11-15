import tools
import config
import geojson
import pandas as pd
from sqlalchemy.sql import text
from datetime import datetime
from dask import delayed



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
        
        
        # take the first 200 agents
        allAgentsInZone = allAgentsInZoneDf["personId"].tolist()
        allAgentsInZone = allAgentsInZone[:200]
        
        
        # Dataframe to store the results
        # the main activity is the activity that takes the most time in the timespan
        activitySequencesDf = pd.DataFrame(columns=["agentId",
                                                    "periodStart",
                                                    "periodEnd",
                                                    "mainActivityId",
                                                    "startActivityId",
                                                    "endActivityId",
                                                    "timeSpentInMainActivity"])
        
        
        # get all activities of all agents in the zone during the given timespan
        print("Getting all activities of all agents in the zone during the given timespan...")
        while startTimeInSeconds < endTimeInSeconds:
            currentEndTimeInSeconds = startTimeInSeconds + intervalInSeconds
            currentStartTimeFormatted = tools.getFormattedTime(startTimeInSeconds)
            currentEndTimeFormatted = tools.getFormattedTime(currentEndTimeInSeconds)
                            
            query = text(f"""SELECT *, 
                                CASE
                                    WHEN :currentStartTimeFormatted <= start_time and :currentEndTimeFormatted >= end_time then end_time - start_time
                                    WHEN :currentStartTimeFormatted >= start_time and :currentEndTimeFormatted >= end_time then end_time - :currentStartTimeFormatted
                                    WHEN :currentStartTimeFormatted > start_time and :currentEndTimeFormatted < end_time then TIME :currentEndTimeFormatted - TIME :currentStartTimeFormatted
                                    WHEN :currentStartTimeFormatted <= start_time and :currentEndTimeFormatted <= end_time then :currentEndTimeFormatted - start_time
                                END as activity_time_spent_in_interval
                            from activity 
                            where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                            and (start_time between :currentStartTimeFormatted and :currentEndTimeFormatted or start_time is null)
                            and (end_time between :currentStartTimeFormatted and :currentEndTimeFormatted or end_time is null)
                            order by start_time asc
                        """)
            
            query = query.bindparams(currentPolygon=currentPolygon, 
                                    currentStartTimeFormatted=currentStartTimeFormatted, 
                                    currentEndTimeFormatted=currentEndTimeFormatted)
            
            currentActivityDf = pd.read_sql(query, conn)
            
            # Retrieve the activity sequences for each agent in the current interval
            # if the agent has no activity in the current interval, we consider that he is doing the same activity as the previous interval
            # if two activities have the same duration, we consider that the first one is the main activity
            for currentAgent in allAgentsInZone:
                currentAgentActivities = currentActivityDf[currentActivityDf["personId"] == currentAgent]
                currentAgentStartActivity = None
                currentAgentEndActivity = None
                currentAgentMainActivity = None
                currentAgentTimeSpentInMainActivity = 0

                if not currentAgentActivities.empty:
                    currentAgentStartActivity = currentAgentActivities.iloc[0]["id"]
                    currentAgentEndActivity = currentAgentActivities.iloc[-1]["id"]
                    currentAgentActivities = currentAgentActivities.sort_values(by=["activity_time_spent_in_interval", "start_time"], ascending=[False, True])
                    currentAgentMainActivity = currentAgentActivities.iloc[0]["id"]
                    currentAgentTimeSpentInMainActivity = currentAgentActivities.iloc[0]["activity_time_spent_in_interval"]
                
                
                
            
            # add interval to startTime
            startTimeInSeconds += intervalInSeconds
                
    print(f"Processed {nbAgentsProcessed} agents in {datetime.now() - agentProcessTimer}")
    return 1
