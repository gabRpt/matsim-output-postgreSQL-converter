import config
import tools
import geojson
import pandas as pd
import collections
from datetime import datetime
from sqlalchemy.sql import text
import dask

# TODO change default interval to 15 minutes
# Return the activity sequences for a every users during a given timespan (by default, 00:00:00 to 32:00:00) 
# with the given interval (by default, 60 minutes)
# in the given zone (geojson file)
 
def activitySequences(filePath, startTime='00:00:00', endTime='32:00:00', interval=60):
    with open(filePath) as f:
        conn = tools.connectToDatabase()
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
                                                                    WHEN '{startTime}' <= start_time and '{endTime}' >= end_time then end_time - start_time
                                                                    WHEN '{startTime}' >= start_time and '{endTime}' >= end_time then end_time - '{startTime}'
                                                                    WHEN '{startTime}' > start_time and '{endTime}' < end_time then TIME '{endTime}' - TIME '{startTime}'
                                                                    WHEN '{startTime}' <= start_time and '{endTime}' <= end_time then '{endTime}' - start_time
                                                                END as activity_time_spent_in_interval
                                                            from activity 
                                                            where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                                                            and (start_time between '{startTime}' and '{endTime}' or start_time is null)
                                                            and (end_time between '{startTime}' and '{endTime}' or end_time is null)
                                                            and "personId" = :currentPersonId
                                                            order by start_time asc
                                                        """)
        
        print("Getting all agents in zone...")
        queryAllAgentsInZone = queryAllAgentsInZone.bindparams(currentPolygon=polygon)
        allAgentsInZoneDf = pd.read_sql(queryAllAgentsInZone, conn)
        
        print(allAgentsInZoneDf)
        # quit()
        
        agentProcessTimer = datetime.now() # timer to measure the time it takes to process all agents
        
        # TODO Remove these lines
        # take the first 200 agents
        allAgentsInZone = allAgentsInZoneDf["personId"].tolist()
        allAgentsInZone = allAgentsInZone[:200]
        
        
        # dictionnary to store the activity sequences for each agent
        # the main activity is the activity that takes the most time in the timespan
        # the keys are: agentId, periodStart, periodEnd, mainActivityId, startActivityId, endActivityId, mainActivityStartTime, mainActivityEndTime, timeSpentInMainActivity
        activitySequencesDf = pd.DataFrame(columns=[
            "agentId",
            "periodStart",
            "periodEnd",
            "mainActivityId",
            "startActivityId",
            "endActivityId",
            "endActivityEndTime",
            "mainActivityStartTime",
            "mainActivityEndTime",
            "timeSpentInMainActivity"
        ])
        
        endTimeInSeconds = tools.getTimeInSeconds(endTime)
        intervalInSeconds = interval * 60
        
        for currentAgentId in allAgentsInZone:
            # get all activities of the current agent in the zone during the given timespan
            # Querying the database to get all activities of the current agent in the zone
            queryGetActivitiesDuringTimeSpanAndZone = queryGetActivitiesDuringTimeSpanAndZone.bindparams(
                currentPolygon=polygon,
                currentPersonId=currentAgentId
            )
            currentActivityDf = pd.read_sql(queryGetActivitiesDuringTimeSpanAndZone, conn)
            
            startTimeInSeconds = tools.getTimeInSeconds(startTime)
            
            # Parse the activities
            currentAgentPreviousStartActivityId = None
            currentAgentPreviousEndActivityId = None
            currentAgentPreviousEndActivityEndTime = None
            currentAgentPreviousMainActivityId = None
            currentAgentPreviousMainActivityStartTime = None
            currentAgentPreviousMainActivityEndTime = None
            currentAgentPreviousTimeSpentInMainActivity = None
            while startTimeInSeconds < endTimeInSeconds:
                currentEndTimeInSeconds = startTimeInSeconds + intervalInSeconds
                currentStartTimeFormatted = tools.getFormattedTime(startTimeInSeconds)
                currentEndTimeFormatted = tools.getFormattedTime(currentEndTimeInSeconds)
                
                currentAgentStartActivityId = None
                currentAgentEndActivityId = None
                currentAgentEndActivityEndTime = None
                currentAgentMainActivityId = None
                currentAgentMainActivityStartTime = None
                currentAgentMainActivityEndTime = None
                currentAgentTimeSpentInMainActivity = None
                
                if currentAgentPreviousEndActivityEndTime is not None:
                    currentAgentPreviousEndActivityEndTimeInSeconds = tools.getTimeInSeconds(currentAgentPreviousEndActivityEndTime)
                else:
                    currentAgentPreviousEndActivityEndTimeInSeconds = tools.getTimeInSeconds(startTime)
                
                # print(f"Processing agent {currentAgentId} from {currentStartTimeFormatted} to {currentEndTimeFormatted}")
                
                activitiesDf = currentActivityDf[(currentActivityDf["start_time"] >= currentStartTimeFormatted) & (currentActivityDf["start_time"] < currentEndTimeFormatted)]
                
                # if the agent has no activity in the current interval, we check if the previous end activity ends during or after
                # the current interval. If it does, we use the previous end activity as the current activity
                if activitiesDf.empty:
                    if currentAgentPreviousEndActivityEndTimeInSeconds >= startTimeInSeconds:
                        currentAgentStartActivityId = currentAgentPreviousEndActivityId
                        currentAgentMainActivityId = currentAgentPreviousEndActivityId
                        currentAgentMainActivityStartTime = currentEndTimeFormatted
                        
                        if currentAgentPreviousEndActivityEndTimeInSeconds >= currentEndTimeInSeconds:
                            # case where the previous end activity ends after the current interval
                            currentAgentTimeSpentInMainActivity = tools.getFormattedTime(intervalInSeconds)
                            currentAgentEndActivityId = currentAgentPreviousEndActivityId
                            currentAgentEndActivityEndTime = currentEndTimeFormatted
                            currentAgentMainActivityEndTime = currentEndTimeFormatted
                        else:
                            # case where the previous end activity ends during the current interval
                            currentAgentTimeSpentInMainActivity = tools.getFormattedTime(currentAgentPreviousEndActivityEndTimeInSeconds - startTimeInSeconds)
                            currentAgentEndActivityId = None
                            currentAgentEndActivityEndTime = None
                            currentAgentMainActivityEndTime = currentAgentPreviousEndActivityEndTime
                    else:
                        # case where the agent has no activity in the current interval and the previous end activity ends before the current interval
                        # we keep all values to None
                        pass
                else:
                    # use the activity that takes the most time in the interval as the main activity
                    mostTimeSpentActivity = activitiesDf[activitiesDf["activity_time_spent_in_interval"] == activitiesDf["activity_time_spent_in_interval"].max()]
                    print(mostTimeSpentActivity)
                    print(activitiesDf)
                    print("=======================================")
                    currentAgentMainActivityId = mostTimeSpentActivity["id"].iloc[0]
                    currentAgentMainActivityStartTime = mostTimeSpentActivity["start_time"].iloc[0]
                    currentAgentMainActivityEndTime = mostTimeSpentActivity["end_time"].iloc[0]
                    currentAgentTimeSpentInMainActivity = mostTimeSpentActivity["activity_time_spent_in_interval"].iloc[0]
                    
                    currentAgentStartActivityId = activitiesDf["id"].iloc[0]
                    currentAgentEndActivityId = activitiesDf["id"].iloc[-1]
                    currentAgentEndActivityEndTime = activitiesDf["end_time"].iloc[-1]                
                
                
                # add the current activity sequence to the dataframe
                # activitySequencesDf = activitySequencesDf.append({
                #     "agentId": currentAgentId,
                #     "periodStart": currentStartTimeFormatted,
                #     "periodEnd": currentEndTimeFormatted,
                #     "mainActivityId": currentAgentMainActivityId,
                #     "startActivityId": currentAgentStartActivityId,
                #     "endActivityId": currentAgentEndActivityId,
                #     "endActivityEndTime": currentAgentEndActivityEndTime,
                #     "mainActivityStartTime": currentAgentMainActivityStartTime,
                #     "mainActivityEndTime": currentAgentMainActivityEndTime,
                #     "timeSpentInMainActivity": currentAgentTimeSpentInMainActivity
                # }, ignore_index=True)
                
                # add interval to startTime
                startTimeInSeconds += intervalInSeconds            
    

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