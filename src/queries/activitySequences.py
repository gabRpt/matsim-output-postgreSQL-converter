import config
import tools
import geojson
import pandas as pd
import collections
from sqlalchemy.sql import text
import multiprocessing as mp

# Return the activity sequences for a every users during a given timespan (by default, 00:00:00 to 32:00:00) 
# with the given interval (by default, 60 minutes)
# in the given zone (geojson file)
# The batchSize parameter is used to speed up the process by splitting the users into batches of batchSize users
def activitySequences(filePath, startTime='00:00:00', endTime='32:00:00', interval=15, batchSize=10):
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
                                                                    WHEN '{startTime}' > start_time and '{endTime}' < end_time then interval '{endTime}' - interval '{startTime}'
                                                                    WHEN '{startTime}' <= start_time and '{endTime}' <= end_time then '{endTime}' - start_time
                                                                    WHEN start_time is null and '{endTime}' >= end_time then end_time - '{startTime}'
                                                                    WHEN start_time is null and '{endTime}' < end_time then interval '{endTime}' - interval '{startTime}'
                                                                    WHEN '{startTime}' > start_time and end_time is null then interval '{endTime}' - interval '{startTime}'
                                                                    WHEN '{startTime}' <= start_time and end_time is null then '{endTime}' - start_time
                                                                    WHEN start_time is null and end_time is null then interval '{endTime}' - interval '{startTime}'
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
        allAgentsInZone = allAgentsInZoneDf["personId"].tolist()
        
        print("Getting all activities during time span and zone...")
        # Querying the database to get all activities of the current agent in the zone
        queryGetActivitiesDuringTimeSpanAndZone = queryGetActivitiesDuringTimeSpanAndZone.bindparams(
            currentPolygon=polygon,
        )

        allActivitiesDf = pd.read_sql(queryGetActivitiesDuringTimeSpanAndZone, conn)        
        
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
        
        
        firstStartTimeInSeconds = tools.getTimeInSeconds(startTime)
        endTimeInSeconds = tools.getTimeInSeconds(endTime)
        intervalInSeconds = interval * 60
        formattedInterval = tools.getFormattedTime(intervalInSeconds)
        
        # Create array with all the start times of the intervals + the end time
        timeList = [x for x in range(0, endTimeInSeconds, intervalInSeconds)] + [endTimeInSeconds]
        formattedTimeList = [tools.getFormattedTime(x) for x in timeList]
        
        # Create a dictionary with the start time of the interval as key and the formatted start time as value
        timeDict = dict(zip(timeList, formattedTimeList))
                
        # Create batches of agents to process in parallel
        batches = [allAgentsInZone[i:i + batchSize] for i in range(0, len(allAgentsInZone), batchSize)]
        
        # Process the batches in parallel
        with mp.Pool(mp.cpu_count()) as pool:
            results = pool.starmap(_getActivitySequencesOfAgentInZoneInTimespanInBatch, [(allActivitiesDf, agentsList, firstStartTimeInSeconds, endTimeInSeconds, intervalInSeconds, formattedInterval, timeDict) for agentsList in batches])
            
            for result in results:
                activitySequencesDict = _mergeActivitySequencesDicts([activitySequencesDict, result])
    
    activitySequencesDf = pd.DataFrame(activitySequencesDict)
    
    return activitySequencesDf



def _getActivitySequencesOfAgentInZoneInTimespanInBatch(allActivitiesDf, agentsList, firstStartTimeInSeconds, endTimeInSeconds, intervalInSeconds, formattedInterval, timeDict):
    activitySequencesDict = collections.defaultdict(list)

    for agent in agentsList:
        currentAgentActivitySequencesDict = _getActivitySequencesOfAgentInZoneInTimespan(allActivitiesDf, agent, firstStartTimeInSeconds, endTimeInSeconds, intervalInSeconds, formattedInterval, timeDict)
        activitySequencesDict = _mergeActivitySequencesDicts([activitySequencesDict, currentAgentActivitySequencesDict])

    return activitySequencesDict



def _getActivitySequencesOfAgentInZoneInTimespan(allActivitiesDf, currentAgentId, firstStartTimeInSeconds, endTimeInSeconds, intervalInSeconds, formattedInterval, timeDict):
    # get all activities of the current agent in the zone during the given timespan
    agentActivitiesDf = allActivitiesDf[allActivitiesDf["personId"] == currentAgentId]
    
    # dictionary with the same structure as the activitySequencesDf
    # the keys are: agentId, periodStart, periodEnd, mainActivityId, startActivityId, endActivityId, mainActivityStartTime, mainActivityEndTime, timeSpentInMainActivity
    agentActivitySequencesDict = collections.defaultdict(list)
    currentStartTimeInSeconds = firstStartTimeInSeconds
    
    # Parse the activities
    currentAgentPreviousEndActivityId = None
    currentAgentPreviousEndActivityEndTime = None
    alreadyAddedNullStartActivity = False

    nullStartTimeActivities = agentActivitiesDf[agentActivitiesDf["start_time"].isnull()]

    while currentStartTimeInSeconds < endTimeInSeconds:
        currentEndTimeInSeconds = currentStartTimeInSeconds + intervalInSeconds
        currentStartTimeFormatted = timeDict[currentStartTimeInSeconds]
        currentEndTimeFormatted = timeDict[currentEndTimeInSeconds]
        
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
            elif type(currentAgentPreviousEndActivityEndTime) is pd._libs.tslibs.nattype.NaTType:
                pass
            else:
                print(f"{currentStartTimeFormatted} - {currentEndTimeFormatted}")
                print(f"{currentAgentId} - {currentAgentPreviousEndActivityEndTime}")
                print(f"unknown type: {type(currentAgentPreviousEndActivityEndTime)}")
        else:
            currentAgentPreviousEndActivityEndTimeInSeconds = -1
            
        activitiesDf = agentActivitiesDf[(agentActivitiesDf["start_time"] >= currentStartTimeFormatted) & (agentActivitiesDf["start_time"] < currentEndTimeFormatted)]
        
        # if the agent has no activity in the current interval, we check if the previous end activity ends during or after
        # the current interval. If it does, we use the previous end activity as the current activity
        if activitiesDf.empty:
            if currentAgentPreviousEndActivityEndTimeInSeconds >= currentStartTimeInSeconds or type(currentAgentPreviousEndActivityEndTime) is pd._libs.tslibs.nattype.NaTType:
                currentAgentStartActivityId = currentAgentPreviousEndActivityId
                currentAgentMainActivityId = currentAgentPreviousEndActivityId
                currentAgentMainActivityStartTime = currentAgentPreviousMainActivityStartTime
                currentAgentMainActivityEndTime = currentAgentPreviousEndActivityEndTime
                
                
                if currentAgentPreviousEndActivityEndTimeInSeconds >= currentEndTimeInSeconds or type(currentAgentPreviousEndActivityEndTime) is pd._libs.tslibs.nattype.NaTType:
                    # case where the previous end activity ends after the current interval
                    currentAgentTimeSpentInMainActivity = formattedInterval
                    currentAgentEndActivityId = currentAgentPreviousEndActivityId
                    currentAgentEndActivityEndTime = currentAgentPreviousEndActivityEndTime
                else:
                    # case where the previous end activity ends during the current interval
                    currentAgentTimeSpentInMainActivity = tools.getFormattedTime(currentAgentPreviousEndActivityEndTimeInSeconds - currentStartTimeInSeconds)
                    currentAgentEndActivityId = None
                    currentAgentEndActivityEndTime = None
            else:
                # case where the agent has no activity in the current interval and the previous end activity ends before the current interval
                                
                if not nullStartTimeActivities.empty and not alreadyAddedNullStartActivity:
                    # case where the agents has a starting activity with no start time
                    currentAgentMainActivityId = nullStartTimeActivities.iloc[0]["id"]
                    currentAgentMainActivityStartTime = nullStartTimeActivities.iloc[0]["start_time"]
                    currentAgentMainActivityEndTime = nullStartTimeActivities.iloc[0]["end_time"]
                    currentAgentTimeSpentInMainActivity = tools.getFormattedTime(intervalInSeconds)
                    currentAgentEndActivityId = currentAgentMainActivityId
                    currentAgentEndActivityEndTime = currentAgentMainActivityEndTime
                    currentAgentStartActivityId = currentAgentMainActivityId
                    alreadyAddedNullStartActivity = True

        else:
            # use the activity that takes the most time in the interval as the main activity
            mostTimeSpentActivity = activitiesDf[activitiesDf["activity_time_spent_in_interval"] == activitiesDf["activity_time_spent_in_interval"].max()]
            
            currentAgentMainActivityId = mostTimeSpentActivity["id"].iloc[0]
            currentAgentMainActivityStartTime = mostTimeSpentActivity["start_time"].iloc[0]
            currentAgentMainActivityEndTime = mostTimeSpentActivity["end_time"].iloc[0]            
            currentAgentStartActivityId = activitiesDf["id"].iloc[0]
            currentAgentEndActivityId = activitiesDf["id"].iloc[-1]
            currentAgentEndActivityEndTime = activitiesDf["end_time"].iloc[-1]
            
            if currentAgentMainActivityEndTime.total_seconds() >= currentEndTimeInSeconds or type(currentAgentMainActivityEndTime) is pd._libs.tslibs.nattype.NaTType:
                currentAgentTimeSpentInMainActivity = tools.getFormattedTime(currentEndTimeInSeconds - currentAgentMainActivityStartTime.total_seconds())
            else:
                currentAgentTimeSpentInMainActivity = tools.getFormattedTime(currentAgentMainActivityEndTime.total_seconds() - currentAgentMainActivityStartTime.total_seconds())
                

        
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
        currentAgentPreviousMainActivityStartTime = currentAgentMainActivityStartTime
        currentAgentPreviousEndActivityId = currentAgentEndActivityId
        currentAgentPreviousEndActivityEndTime = currentAgentEndActivityEndTime
        
        # add interval to startTime
        currentStartTimeInSeconds += intervalInSeconds
    
    # create the dataframe
    return agentActivitySequencesDict



# Merge a list of activity sequences dictionaries into a single dictionary
def _mergeActivitySequencesDicts(activitySequencesDicts):
    mergedActivitySequencesDict = collections.defaultdict(list)
    for activitySequencesDict in activitySequencesDicts:
        for key, value in activitySequencesDict.items():
            mergedActivitySequencesDict[key].extend(value)
    return mergedActivitySequencesDict