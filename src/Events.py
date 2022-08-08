import matsim.Events as Events
import matsim.Network as Network
import config
import tools
import pandas as pd
import collections
import math


def importEvents(timeStepInMinutes=60, useRoundedTime=True, displayHoursInsteadOfSeconds=True):
    eventsResultsDataframe = _getEventsVehicleCountAndMeanSpeed(timeStepInMinutes, useRoundedTime, displayHoursInsteadOfSeconds)
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    eventsResultsDataframe.to_sql('networkLinkTraffic', con=conn, if_exists='append', index=False)
    



# TODO: Review the case where a vehicle enters a link at the same time as it leaves it
# TODO: Review the case where the mean speed of a vehicle is greater than the speed limit of the link it is on
# TODO: Review the case where the mean speed is 0
# TODO: Take into account public transport events
# TODO: Implement vehicle filter option, (e.g. same output but with vehicleCount and meanSpeed for specified vehicle type)
# returns a dataframe with, for each link, the vehicle count and mean speed every x minutes set in parameter
# if useRoundedTime is True => if the first event is at time '12613' (3.5h) => it will start at time '10800' (3h)
# if displayHoursInsteadOfSeconds is True => for a timespan between '10800' and '12600' => it will display '3:00:00' and '3:30:00'
def _getEventsVehicleCountAndMeanSpeed(timeStepInMinutes=60, useRoundedTime=True, displayHoursInsteadOfSeconds=True):
    timeStepInSeconds = timeStepInMinutes * 60
    
    events = Events.event_reader(config.PATH_EVENTS)    
    eventsDataframe = pd.DataFrame(events)
    
    network = Network.read_network(config.PATH_NETWORK)
    networkLinksDataframe = network.links
    networkLinksLengthDict = dict(zip(networkLinksDataframe['link_id'], networkLinksDataframe['length']))
    networkLinksFreespeedDict = dict(zip(networkLinksDataframe['link_id'], networkLinksDataframe['freespeed']))
    
    linksEntryKeyWords = ['entered link', 'departure', 'VehicleDepartsAtFacility']
    linksExitKeyWords = ['left link', 'arrival']
    
    # keeping only useful events
    eventsDataframe = eventsDataframe[eventsDataframe['type'].isin(linksEntryKeyWords + linksExitKeyWords)]

    # Removing starting and ending events not using car as mode
    # and events using pt
    eventsDataframe.drop(eventsDataframe[
        ((eventsDataframe['type'] == 'departure') | (eventsDataframe['type'] == 'arrival')) &
        ((eventsDataframe['legMode'] != 'car') | (eventsDataframe['person'].astype(str).str.startswith('pt')))
    ].index, inplace=True)

    
    # Adding link to the events where the link is stored in facility column where link type is VehicleDepartsAtFacility
    # ex facility="SNCF:87590331.link:pt_SNCF:87590331" -> link="pt_SNCF:87590331"
    # ex facility="22167-R.link:40411" -> link="40411"
    eventsDataframe.loc[(eventsDataframe['type'] == 'VehicleDepartsAtFacility') &
                        (eventsDataframe['vehicle'].str.split('_').str[-1] != 'tram'), 'link'] = eventsDataframe['facility'].str.split(':').str[-1]
    
    eventsDataframe.loc[(eventsDataframe['type'] == 'VehicleDepartsAtFacility') &
                        (eventsDataframe['vehicle'].str.split('_').str[-1] == 'tram'), 'link'] = eventsDataframe['facility'].str.split('link:').str[-1]
        
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

                if displayHoursInsteadOfSeconds:
                    timespan = f'{tools.getFormattedTime(currentStartingTime)}_{tools.getFormattedTime(currentEndingTime)}'
                else:
                    timespan = f'{int(currentStartingTime)}_{int(currentEndingTime)}'
                
                # Checking if meanspeed is above links freespeed limit
                if meanSpeed > networkLinksFreespeedDict[linkId]:
                    meanSpeed = networkLinksFreespeedDict[linkId]
                
                resultsDict['linkId'].append(linkId)
                resultsDict['timeSpan'].append(timespan)
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
                except Exception:
                    startingTimeInLink = row.time
                    print(f'Error: link {row.link} has an empty queue')
                
                secondsSpentInLink = row.time - startingTimeInLink
                
                # Calculating the mean speed in the link (in meter/second)
                linkLength = networkLinksLengthDict[row.link]
                try:
                    speed = linkLength / secondsSpentInLink
                except Exception:   # Case if a vehicle leaves the link at the same time it enters
                    speed = 0
                    # print(f'Error: \nlink => {row.link} \nlinkLength => {linkLength} \nsecondsSpentInLink => {secondsSpentInLink} \nstartingTimeInLink => {startingTimeInLink} \nrow.time => {row.time} \ntype => {row.type} \nlegMode => {row.legMode}')
                meanSpeedInLinksDict[row.link].append(speed)
                vehiclesPerLinkDict[row.link] += 1
                
            else:
                print(f'Error: link {row.link} not found in the queue person: {row.person} / legMode: {row.legMode}')

    resultsDict = pd.DataFrame(resultsDict)
    return resultsDict