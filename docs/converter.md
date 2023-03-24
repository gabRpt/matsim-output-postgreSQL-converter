# Converter

___

```python
from furbain import converter
```
___

## How to

The converter is used to get the output data from matsim, process it and load it into a PostgreSQL database.  

To use the converter you have to setup the simulation output path. `setSimulationOutputPath(path)`  
You also may have to setup the output files names if they are different than the one described in the `configuration` section of the documentation. Look at `setVariableInConfigurationFile(name, value)`.


Then you can user the converter to import the tables you want :

| Table name  | Converter function to use |
| ------------- | ------------- |
| activity  | converter.activities.importActivities() |
| building | converter.buildings.importBuildings() |
| facility | converter.facilities.importFacilities() |
| household | converter.households.importHouseholds() |
| networdlink | converter.networkLinks.importNetworkLinks(useDetailedNetworkFile=True) |
| networdlinkTraffic | converter.events.importEvents(timeStepInMinutes=60, useRoundedTime=True) |
| person  | converter.persons.importPersons() |
| trip | converter.trips.importTrips() |
| vehicle | converter.vehicles.importVehicles() |
| vehicleType | converter.vehicles.importVehicles() |

## Specificities

The function `importNetworkLinks()` has one parameter :
* `useDetailedNetworkFile` : a boolean that defines if the detailed network file should be used to generate the network links table. _The default value is True._

The function `importEvents()` has two parameters :
* `timeStepInMinutes`  : an integer that defines the time step used to aggregate the events. _The default value is 60 minutes._
* `useRoundedTime` : a boolean that defines if the starting time should be round, or if the time should be the exact time of the event. Eg: The first event starts at 12:36:01, timeStepInMinutes is set at 60. **If set True** the first time step will be 12:00:00 to 13:00:00. **If set False**, it will be 12:36:01 to 13:36:01. _The default value is True._

## Example
Code example for tables importation :

```python
from datetime import datetime
from furbain import converter
from furbain import config


def main():
    overallStartTime = datetime.now()

    config.setSimulationOutputPath('C:/Users/name/Documents/Furbain/data/matsim_nantes_edgt_20p/simulation_output')

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

```