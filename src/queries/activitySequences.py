import config
import tools
import geojson
import pandas as pd
import collections
from datetime import datetime
from sqlalchemy.sql import text


# TODO change default interval to 15 minutes
# Return the activity sequences for a every users during a given timespan (by default, 00:00:00 to 32:00:00) 
# with the given interval (by default, 60 minutes)
# in the given zone (geojson file)

def activitySequences(filePath, startTime='00:00:00', endTime='32:00:00', interval=60):
    conn = tools.connectToDatabase()
    
    startTimeInSeconds = tools.getTimeInSeconds(startTime)
    endTimeInSeconds = tools.getTimeInSeconds(endTime)
    intervalInSeconds = interval * 60
    
    with open(filePath) as f:
        gjson = geojson.load(f)
        
        geojsonEpsg = tools.getEPSGFromGeoJSON(gjson)
                
        geometry = gjson["features"][0]["geometry"]
        coordinates = geometry["coordinates"]
        geometryType = geometry["type"]
        polygon = tools.formatGeoJSONPolygonToPostgisPolygon(coordinates, geometryType, geojsonEpsg)
        
        # QUERIES
        queryAllAgentsInZone = text(f"""SELECT distinct "personId"
                                        from activity
                                        where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                                    """)
        
        queryGetActivitiesDuringTimeSpanAndZone = text(f"""SELECT *, 
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
        
        print("Getting all agents in zone...")
        queryAllAgentsInZone = queryAllAgentsInZone.bindparams(currentPolygon=polygon)
        allAgentsInZoneDf = pd.read_sql(queryAllAgentsInZone, conn)
        
        
        agentProcessTimer = datetime.now() # timer to measure the time it takes to process all agents
        
        # TODO Remove these lines
        # take the first 200 agents
        allAgentsInZone = allAgentsInZoneDf["personId"].tolist()
        allAgentsInZone = allAgentsInZone[:200]
        
        
        # dictionnary to store the activity sequences for each agent
        # the main activity is the activity that takes the most time in the timespan
        # the keys are: agentId, periodStart, periodEnd, mainActivityId, startActivityId, endActivityId, maintActivityStartTime, maintActivityEndTime, timeSpentInMainActivity
        activitySequencesDict = collections.defaultdict(list)
        
        
        # get all activities of all agents in the zone during the given timespan
        print("Getting all activities of all agents in the zone during the given timespan...")
        while startTimeInSeconds < endTimeInSeconds:
            currentEndTimeInSeconds = startTimeInSeconds + intervalInSeconds
            currentStartTimeFormatted = tools.getFormattedTime(startTimeInSeconds)
            currentEndTimeFormatted = tools.getFormattedTime(currentEndTimeInSeconds)
            
            # Querying the database for all agents in the zone
            queryGetActivitiesDuringTimeSpanAndZone = queryGetActivitiesDuringTimeSpanAndZone.bindparams(
                currentPolygon=polygon, 
                currentStartTimeFormatted=currentStartTimeFormatted, 
                currentEndTimeFormatted=currentEndTimeFormatted
            )
            currentActivityDf = pd.read_sql(queryGetActivitiesDuringTimeSpanAndZone, conn)
            
            # retrieve activity sequences for each agent
            for currentAgentId in allAgentsInZone:
                activitySequencesDict = _retrieveActivitiesOfEachAgentsDuringGivenInterval(currentAgentId, currentActivityDf, activitySequencesDict, startTimeInSeconds, endTimeInSeconds, currentStartTimeFormatted, currentEndTimeFormatted)
                
            # add interval to startTime
            startTimeInSeconds += intervalInSeconds
    
    # activitySequencesDict = activitySequencesDict.compute()
    activitySequencesDf = pd.DataFrame(activitySequencesDict)
    agent95254Activities = activitySequencesDf[activitySequencesDf["agentId"] == 95254]
    
    print(activitySequencesDf)
    print(agent95254Activities)
    print(f"Time: {datetime.now() - agentProcessTimer}")
    return 1


# Retrieve the activity sequences for each agent in the current interval
# if the agent has no activity in the current interval, we consider that he is doing the same activity as the previous interval
# if two activities have the same duration, we consider that the first one is the main activity
def _retrieveActivitiesOfEachAgentsDuringGivenInterval(currentAgentId, currentActivityDf, activitySequencesDict, startTimeInSeconds, endTimeInSeconds, currentStartTimeFormatted, currentEndTimeFormatted):
    currentAgentActivities = currentActivityDf[currentActivityDf["personId"] == currentAgentId]
    currentAgentStartActivity = None
    currentAgentEndActivity = None
    currentAgentMainActivity = None
    currentAgentMainActivityStartTime = None
    currentAgentMainActivityEndTime = None
    currentAgentTimeSpentInMainActivity = '00:00:00'

    if not currentAgentActivities.empty:
        currentAgentStartActivity = currentAgentActivities.iloc[0]["id"]
        currentAgentEndActivity = currentAgentActivities.iloc[-1]["id"]
        currentAgentActivities = currentAgentActivities.sort_values(by=["activity_time_spent_in_interval", "start_time"], ascending=[False, True])
        currentAgentMainActivity = currentAgentActivities.iloc[0]["id"]
        currentAgentTimeSpentInMainActivity = currentAgentActivities.iloc[0]["activity_time_spent_in_interval"]
        currentAgentMainActivityStartTime = currentAgentActivities.iloc[0]["start_time"]
        currentAgentMainActivityEndTime = currentAgentActivities.iloc[0]["end_time"]
        
    elif currentAgentId in activitySequencesDict["agentId"]:
        index = len(activitySequencesDict["agentId"]) - 1 - activitySequencesDict["agentId"][::-1].index(currentAgentId)
        
        # check if the previous main activity end time is in the current interval
        # if yes, we consider that the agent is doing the same activity as the previous interval
        previousMainActivityEndTime = activitySequencesDict["maintActivityEndTime"][index]
        
        if previousMainActivityEndTime is not None:
            previousMainActivityEndTimeInSeconds = tools.getTimeInSeconds(previousMainActivityEndTime)
            if previousMainActivityEndTimeInSeconds is not None and previousMainActivityEndTimeInSeconds >= startTimeInSeconds and previousMainActivityEndTimeInSeconds <= endTimeInSeconds:
                timeSpentInMainActivityInSeconds = previousMainActivityEndTimeInSeconds - startTimeInSeconds
                currentAgentMainActivity = activitySequencesDict["mainActivityId"][index]
                currentAgentTimeSpentInMainActivity = activitySequencesDict["timeSpentInMainActivity"][index]
                currentAgentStartActivity = activitySequencesDict["startActivityId"][index]
                currentAgentMainActivityEndTime = activitySequencesDict["maintActivityEndTime"][index]
                currentAgentMainActivityStartTime = activitySequencesDict["maintActivityStartTime"][index]
                
                if timeSpentInMainActivityInSeconds is not None and timeSpentInMainActivityInSeconds > 0: 
                    currentAgentEndActivity = activitySequencesDict["endActivityId"][index]
                else:
                    currentAgentEndActivity = None
    
    activitySequencesDict["agentId"].append(currentAgentId)
    activitySequencesDict["periodStart"].append(currentStartTimeFormatted)
    activitySequencesDict["periodEnd"].append(currentEndTimeFormatted)
    activitySequencesDict["mainActivityId"].append(currentAgentMainActivity)
    activitySequencesDict["startActivityId"].append(currentAgentStartActivity)
    activitySequencesDict["endActivityId"].append(currentAgentEndActivity)
    activitySequencesDict["maintActivityStartTime"].append(currentAgentMainActivityStartTime)
    activitySequencesDict["maintActivityEndTime"].append(currentAgentMainActivityEndTime)
    activitySequencesDict["timeSpentInMainActivity"].append(currentAgentTimeSpentInMainActivity)
        
    return activitySequencesDict