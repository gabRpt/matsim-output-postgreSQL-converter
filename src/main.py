import converter
from datetime import datetime


def main():
    overallStartTime = datetime.now()
    tablesToImport = [
        # "vehicles",
        # "households",
        # "persons",
        "networkLinks",
        # "facilities",
        # "trips",
        # "activities",
        # "events",
    ]
    
    print("========== STARTING IMPORTATIONS ==========")
    
    for table in tablesToImport:
        launchImport(table)
    
    print(f"========== IMPORTED IN {str(datetime.now() - overallStartTime)[:-5]} ==========")


def launchImport(name):
    currentStartTime = datetime.now()
    print(f"Importing {name}...", end="", flush=True)
    
    if name == "vehicles":
        converter.importVehicles()
    elif name == "households":
        converter.importHouseholds()
    elif name == "persons":
        converter.importPersons()
    elif name == "networkLinks":
        converter.importNetworkLinks()
    elif name == "facilities":
        converter.importFacilities()
    elif name == "trips":
        converter.importTrips()
    elif name == "activities":
        converter.importActivities()
    elif name == "events":
        converter.importEvents()
    
    print(f" Done in {str(datetime.now() - currentStartTime)[:-5]} !")


main()