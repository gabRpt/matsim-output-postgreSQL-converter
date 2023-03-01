import matsim.Events as Events
import matsim.Network as Network
from furbain import config
from furbain import tools
import pandas as pd
import collections
import math


def importEvents(timeStepInMinutes=60, useRoundedTime=True):
    eventsResultsDataframe = _getEventsVehicleCountAndMeanSpeed(timeStepInMinutes, useRoundedTime)
    
    # Creating the tables in the database
    _createEventsTable()
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    eventsResultsDataframe.to_sql(config.DB_EVENTS_TABLE, con=conn, if_exists='append', index=False)
    conn.close()
    

def _createEventsTable():
    conn = tools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_EVENTS_TABLE}" (
            "linkId" character varying(40) COLLATE pg_catalog."default" NOT NULL,
            "startTime" interval NOT NULL,
            "endTime" interval NOT NULL,
            "vehicleCount" integer,
            "meanSpeed" double precision,
            CONSTRAINT "networkLinkTraffic_pkey" PRIMARY KEY ("linkId", "startTime", "endTime")
        );
    """)
    conn.close()


# TODO: Take into account public transport events
# TODO: Implement vehicle filter option, (e.g. same output but with vehicleCount and meanSpeed for specified vehicle type)
# returns a dataframe with, for each link, the vehicle count and mean speed every x minutes set in parameter
def _getEventsVehicleCountAndMeanSpeed(timeStepInMinutes=60, useRoundedTime=True):
    timeStepInSeconds = timeStepInMinutes * 60
    
    events = Events.event_reader(config.PATH_EVENTS)    
    eventsDataframe = pd.DataFrame(events)
    
    network = Network.read_network(config.PATH_NETWORK)
    networkLinksDataframe = network.links
    networkLinksLengthDict = dict(zip(networkLinksDataframe['link_id'], networkLinksDataframe['length']))
    networkLinksFreespeedDict = dict(zip(networkLinksDataframe['link_id'], networkLinksDataframe['freespeed']))
    
    linksEntryKeyWords = ['entered link']
    linksExitKeyWords = ['left link']
    
    # keeping only useful events
    eventsDataframe = eventsDataframe[eventsDataframe['type'].isin(linksEntryKeyWords + linksExitKeyWords)]
    eventsDataframe.reset_index(drop=True, inplace=True)
        
    # Calculating the number of vehicles in each link at each time step
    # Calculating the mean speed of each link at each time step
    if useRoundedTime:
        currentStartingTime = math.floor(eventsDataframe['time'][0] / 3600) * 3600
        while eventsDataframe['time'][0] > currentStartingTime:
            currentStartingTime += timeStepInSeconds
        currentStartingTime -= timeStepInSeconds
    else: 
        currentStartingTime = eventsDataframe['time'][0]
    
    currentEndingTime = currentStartingTime + timeStepInSeconds

    enteredLinksQueueDict = collections.defaultdict(list)
    meanSpeedInLinksDict = collections.defaultdict(list)
    vehiclesPerLinkDict = collections.defaultdict(int)
    resultsDict = collections.defaultdict(list)
    
    # Parsing the events
    for row in eventsDataframe.itertuples():
        # Checking if we are still in the current time span
        if row.time > currentEndingTime:
            for linkId, speeds in meanSpeedInLinksDict.items():
                vehicleCount = vehiclesPerLinkDict[linkId] 
                speeds = [i for i in speeds if i != 0] # removing 0 values
                meanSpeed = sum(speeds) / vehicleCount if vehicleCount > 0 else 0
                
                formattedStartingTime = tools.formatTimeToIntervalType(tools.getFormattedTime(currentStartingTime))
                formattedEndingTime = tools.formatTimeToIntervalType(tools.getFormattedTime(currentEndingTime))

                resultsDict['linkId'].append(linkId)
                resultsDict['startTime'].append(formattedStartingTime)
                resultsDict['endTime'].append(formattedEndingTime)
                resultsDict['vehicleCount'].append(vehicleCount)
                resultsDict['meanSpeed'].append(meanSpeed)
            
            meanSpeedInLinksDict.clear()
            vehiclesPerLinkDict.clear()
            currentStartingTime = currentEndingTime
            currentEndingTime = currentEndingTime + timeStepInSeconds
        
        if row.type in linksEntryKeyWords:
            enteredLinksQueueDict[row.link].append(row.time)
        else:
            if row.link in enteredLinksQueueDict:
                # Calculating time spent in the link
                try: 
                    startingTimeInLink = enteredLinksQueueDict[row.link].pop(0)
                    secondsSpentInLink = row.time - startingTimeInLink
            
                    # Calculating the mean speed in the link (in meter/second)
                    linkLength = networkLinksLengthDict[row.link]
                    try:
                        speed = linkLength / secondsSpentInLink
                        
                        # Checking if meanspeed is above links freespeed limit
                        if speed > networkLinksFreespeedDict[row.link]:
                            # print(f'Warning: speed {speed} > freespeed {networkLinksFreespeedDict[row.link]} for link {row.link}')
                            raise ValueError('Speed above freespeed limit')
                        
                    except Exception:
                        # Case if a vehicle leaves the link at the same time it enters
                        # print(f'Error: \nlink => {row.link} \nlinkLength => {linkLength} \nsecondsSpentInLink => {secondsSpentInLink} \nstartingTimeInLink => {startingTimeInLink} \nrow.time => {row.time} \ntype => {row.type} \nlegMode => {row.legMode}')
                        continue
                    
                    meanSpeedInLinksDict[row.link].append(speed)
                    vehiclesPerLinkDict[row.link] += 1

                except Exception:
                    # skipping the event if the vehicle has not entered the link
                    # print(f'Error: link {row.link} has an empty queue at time {row.time}')
                    continue
            else:
                # skipping the event if the vehicle has not entered the link yet
                # print(f'Error: link {row.link} not found in the queue person: {row.person} / legMode: {row.legMode}')
                continue

    resultsDict = pd.DataFrame(resultsDict)
    return resultsDict