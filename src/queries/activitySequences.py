import config
import tools
import geojson
import pandas as pd
import collections
from datetime import datetime
from sqlalchemy.sql import text
from dask import delayed

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
                                                                    ELSE '{endTime}' - start_time
                                                                END as activity_time_spent_in_interval
                                                            from activity 
                                                            where ST_Contains(ST_Transform(ST_GeomFromText(:currentPolygon, {geojsonEpsg}), {config.DB_SRID}), ST_SetSRID("location", {config.DB_SRID}))
                                                            and (start_time between '{startTime}' and '{endTime}' or start_time is null)
                                                            and (end_time between '{startTime}' and '{endTime}' or end_time is null)
                                                            order by start_time asc
                                                        """)
        
        print("Getting all agents in zone...")
        queryAllAgentsInZone = queryAllAgentsInZone.bindparams(currentPolygon=polygon)
        allAgentsInZoneDf = pd.read_sql(queryAllAgentsInZone, conn)
        
        print("Getting all activities during time span and zone...")
        # Querying the database to get all activities of the current agent in the zone
        queryGetActivitiesDuringTimeSpanAndZone = queryGetActivitiesDuringTimeSpanAndZone.bindparams(
            currentPolygon=polygon,
        )
        allActivitiesDf = pd.read_sql(queryGetActivitiesDuringTimeSpanAndZone, conn)
                
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
        
        activitySequencesDict = collections.defaultdict(list)
        
        
        endTimeInSeconds = tools.getTimeInSeconds(endTime)
        intervalInSeconds = interval * 60
        
        for currentAgentId in allAgentsInZone:
            currentAgentActivitySequencesDict = delayed(_getActivitySequencesOfAgentInZoneInTimespan)(allActivitiesDf, currentAgentId, startTime, endTimeInSeconds, intervalInSeconds)
            activitySequencesDict = delayed(_mergeActivitySequencesDicts)([activitySequencesDict, currentAgentActivitySequencesDict])
            
    # wait for all the delayed functions to finish
    activitySequencesDict = activitySequencesDict.compute()
    activitySequencesDf = pd.DataFrame(activitySequencesDict)
    agent95254Activities = activitySequencesDf[activitySequencesDf["agentId"] == 95254]
    
    print(activitySequencesDf)
    print(agent95254Activities)
    print(f"Time: {datetime.now() - agentProcessTimer}")
    
    # TODO start_time at None
    # TODO remove unsued variables
    return 1


def _getActivitySequencesOfAgentInZoneInTimespan(allActivitiesDf, currentAgentId, startTime, endTimeInSeconds, intervalInSeconds):
    functionTimer = datetime.now()
    # get all activities of the current agent in the zone during the given timespan
    currentActivityDf = allActivitiesDf[allActivitiesDf["personId"] == currentAgentId]
    
    
    # dictionary with the same structure as the activitySequencesDf
    # the keys are: agentId, periodStart, periodEnd, mainActivityId, startActivityId, endActivityId, mainActivityStartTime, mainActivityEndTime, timeSpentInMainActivity
    agentActivitySequencesDict = collections.defaultdict(list)
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
            if type(currentAgentPreviousEndActivityEndTime) is str:
                currentAgentPreviousEndActivityEndTimeInSeconds = tools.getTimeInSeconds(currentAgentPreviousEndActivityEndTime)
            elif type(currentAgentPreviousEndActivityEndTime) is pd._libs.tslibs.timedeltas.Timedelta:
                currentAgentPreviousEndActivityEndTimeInSeconds = int(currentAgentPreviousEndActivityEndTime.total_seconds())
            else:
                print(f"unknown type: {type(currentAgentPreviousEndActivityEndTime)}")
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

            currentAgentMainActivityId = mostTimeSpentActivity["id"].iloc[0]
            currentAgentMainActivityStartTime = mostTimeSpentActivity["start_time"].iloc[0]
            currentAgentMainActivityEndTime = mostTimeSpentActivity["end_time"].iloc[0]
            currentAgentTimeSpentInMainActivity = mostTimeSpentActivity["activity_time_spent_in_interval"].iloc[0]
            currentAgentStartActivityId = activitiesDf["id"].iloc[0]
            currentAgentEndActivityId = activitiesDf["id"].iloc[-1]
            currentAgentEndActivityEndTime = activitiesDf["end_time"].iloc[-1]
        
        # add the current activity sequence to the dictionary
        agentActivitySequencesDict["agentId"].append(currentAgentId)
        agentActivitySequencesDict["periodStart"].append(currentStartTimeFormatted)
        agentActivitySequencesDict["periodEnd"].append(currentEndTimeFormatted)
        agentActivitySequencesDict["mainActivityId"].append(currentAgentMainActivityId)
        agentActivitySequencesDict["startActivityId"].append(currentAgentStartActivityId)
        agentActivitySequencesDict["endActivityId"].append(currentAgentEndActivityId)
        agentActivitySequencesDict["mainActivityStartTime"].append(currentAgentMainActivityStartTime)
        agentActivitySequencesDict["mainActivityEndTime"].append(currentAgentMainActivityEndTime)
        agentActivitySequencesDict["timeSpentInMainActivity"].append(currentAgentTimeSpentInMainActivity)
        
        # update the previous values
        currentAgentPreviousStartActivityId = currentAgentStartActivityId
        currentAgentPreviousEndActivityId = currentAgentEndActivityId
        currentAgentPreviousEndActivityEndTime = currentAgentEndActivityEndTime
        currentAgentPreviousMainActivityId = currentAgentMainActivityId
        currentAgentPreviousMainActivityStartTime = currentAgentMainActivityStartTime
        currentAgentPreviousMainActivityEndTime = currentAgentMainActivityEndTime
        currentAgentPreviousTimeSpentInMainActivity = currentAgentTimeSpentInMainActivity
        
        # add interval to startTime
        startTimeInSeconds += intervalInSeconds
    
    # create the dataframe
    print(f"Function took {datetime.now() - functionTimer} to run")
    return agentActivitySequencesDict

# Merge a list of activity sequences dictionaries into a single dictionary
def _mergeActivitySequencesDicts(activitySequencesDicts):
    mergedActivitySequencesDict = collections.defaultdict(list)
    for activitySequencesDict in activitySequencesDicts:
        for key, value in activitySequencesDict.items():
            mergedActivitySequencesDict[key].extend(value)
    return mergedActivitySequencesDict