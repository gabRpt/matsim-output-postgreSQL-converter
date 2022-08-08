import converter as converter
from datetime import datetime


def main():
    overallStartTime = datetime.now()
    
    # Imports in the right order to avoid foreign key constraints
    tablesToImport = [
        # "vehicles",
        # "households",
        # "persons",
        # "networkLinks",
        # "facilities",
        # "trips",
        # "activities",
        # "events",
        "buildings",
    ]
    
    print("========== STARTING IMPORTATIONS ==========")
    
    for table in tablesToImport:
        launchImport(table)
    
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
        converter.events.importEvents()
    elif name == "buildings":
        converter.buildings.importBuildings()
    
    print(f" Done in {str(datetime.now() - currentStartTime)[:-5]} !")


main()