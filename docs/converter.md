# Converter

___

```python
from furbain import converter
```
___

## How to

The converter is used to get the output data from matsim, process it and load it into a PostgreSQL database.  
To use the converter you have to setup the simulation output path :
```python
config.PATH_SIMULATION_OUTPUT = 'C:/Users/name/Documents/Furbain/data/matsim_nantes_edgt_20p/simulation_output'
```

You also may have to setup the output files names if they are different than the following :
```python
    config.PATH_ALLVEHICLES = config.PATH_SIMULATION_OUTPUT + '/output_allvehicles.xml.gz'
    config.PATH_EVENTS = config.PATH_SIMULATION_OUTPUT + '/output_events.xml.gz'
    config.PATH_FACILITIES = config.PATH_SIMULATION_OUTPUT + '/output_facilities.xml.gz'
    config.PATH_HOUSEHOLDS = config.PATH_SIMULATION_OUTPUT + '/output_households.xml.gz'
    config.PATH_LEGS = config.PATH_SIMULATION_OUTPUT + '/output_legs.csv.gz'
    config.PATH_NETWORK = config.PATH_SIMULATION_OUTPUT + '/output_network.xml.gz'
    config.PATH_PERSONS = config.PATH_SIMULATION_OUTPUT + '/output_persons.csv.gz'
    config.PATH_PLANS = config.PATH_SIMULATION_OUTPUT + '/output_plans.xml.gz'
    config.PATH_EXPERIENCED_PLANS = config.PATH_SIMULATION_OUTPUT + '/output_experienced_plans.xml.gz'
    config.PATH_TRIPS = config.PATH_SIMULATION_OUTPUT + '/output_trips.csv.gz'
    config.PATH_DETAILED_NETWORK = config.PATH_SIMULATION_OUTPUT + '/detailed_network.csv'
    config.PATH_BUILDINGS = config.PATH_SIMULATION_OUTPUT + '/BUILDINGS.geojson'
    config.ARABESQUE_GENERATED_FILES_DIRECTORY_PATH = './'
```

Then you can user the converter to import the tables you want :

| Table name  | Converter function to use |
| ------------- | ------------- |
| activity  | converter.activities.importActivities() |
| building | converter.buildings.importBuildings() |
| facility | converter.facilities.importFacilities() |
| household | converter.households.importHouseholds() |
| networdlink | converter.networkLinks.importNetworkLinks() |
| networdlinkTraffic | converter.events.importEvents() |
| person  | converter.persons.importPersons() |
| trip | converter.trips.importTrips() |
| vehicle | converter.vehicles.importVehicles() |
| vehicleType | converter.vehicles.importVehicles() |

## Specificities

The function `importEvents()` has two parameters :
* `timeStepInMinutes`  : an integer that defines the time step used to aggregate the events. _The default value is 60 minutes._
* `useRoundedTime` : a boolean that defines if the starting time should be round, or if the time should be the exact time of the event. Eg: The first event starts at 12:36:01, timeStepInMinutes is set at 60. **If set True** the first time step will be 12:00:00 to 13:00:00. **If set False**, it will be 12:36:01 to 13:36:01. _The default value is True._

The function `importNetworkLinks()` has one parameter :
* `useDetailedNetworkFile` : a boolean that defines if the detailed network file should be used to generate the network links table. _The default value is True._

## Example
Code example for tables importation :

```python
from datetime import datetime
from furbain import converter
from furbain import config


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


config.PATH_SIMULATION_OUTPUT = 'C:/Users/name/Documents/Furbain/data/matsim_nantes_edgt_20p/simulation_output'

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