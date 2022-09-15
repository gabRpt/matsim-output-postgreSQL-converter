import converter as converter
import queries as queries
from datetime import datetime


def main():
    overallStartTime = datetime.now()
    
    # Imports in the right order to avoid foreign key constraints
    tablesToImport = [
        "vehicles",
        "households",
        "persons",
        "networkLinks",
        "facilities",
        "trips",
        "activities",
        "events",
        "buildings",
    ]
    
    print("========== STARTING IMPORTATIONS ==========")
    
    # for table in tablesToImport:
    #     launchImport(table)
    
    queries.odMatrix.odMatrix("./resources/5zones.geojson", startTime='14:30:00', endTime='15:00:00', ignoreArrivalTime=True, generateArabesqueFiles=True)
    # queries.agentActivity.agentActivity("./resources/5zones.geojson", startTime='18:00:00', endTime='19:00:00', strictTime=False)
    
    print(f"========== IMPORTED IN {str(datetime.now() - overallStartTime)[:-5]} ==========")


def launchImport(name):
    currentStartTime = datetime.now()
    print(f"Importing {name}...", end="", flush=True)
    
    if name == "vehicles":
        converter.vehicles.importVehicles()
    elif name == "households":
        converter.households.importHouseholds()
    elif name == "persons":
        converter.persons.importPersons()
    elif name == "networkLinks":
        converter.networkLinks.importNetworkLinks()
    elif name == "facilities":
        converter.facilities.importFacilities()
    elif name == "trips":
        converter.trips.importTrips()
    elif name == "activities":
        converter.activities.importActivities()
    elif name == "events":
        converter.events.importEvents(timeStepInMinutes=10)
    elif name == "buildings":
        converter.buildings.importBuildings()
    
    print(f" Done in {str(datetime.now() - currentStartTime)[:-5]} !")


main()