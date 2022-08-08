import Vehicles
import Households
import Persons
import NetworkLinks
import Facilities
import Trips
import Activities
import Events
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
        Vehicles.importVehicles()
    elif name == "households":
        Households.importHouseholds()
    elif name == "persons":
        Persons.importPersons()
    elif name == "networkLinks":
        NetworkLinks.importNetworkLinks()
    elif name == "facilities":
        Facilities.importFacilities()
    elif name == "trips":
        Trips.importTrips()
    elif name == "activities":
        Activities.importActivities()
    elif name == "events":
        Events.importEvents()
    
    print(f" Done in {str(datetime.now() - currentStartTime)[:-5]} !")


main()