# Converter

___

Code example for tables importation :

```python
from datetime import datetime
from furbain import converter


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
for table in tablesToImport:
    launchImport(table)
print(f"========== IMPORTED IN {str(datetime.now() - overallStartTime)[:-5]} ==========")

```