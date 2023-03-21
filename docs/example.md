# Example

___

## Package usage example

```python
from datetime import datetime
from furbain import queries
from furbain import converter
from furbain import config
from furbain import databaseTools
import geopandas as gpd


def main():
    overallStartTime = datetime.now()
    
    config.setSimulationOutputPath('C:/Users/name/Documents/Furbain/data/matsim_nantes_edgt_20p/simulation_output')
    config.setVariableInConfigurationFile('allvehicles_filename','/output_allvehicles.xml.gz')

    config.ARABESQUE_GENERATED_FILES_DIRECTORY_PATH = './'
    
    config.setDatabaseUser("postgres")
    config.setDatabasePassword("postgres")
    config.setDatabaseHost("localhost")
    config.setDatabasePort("5432")
    config.setDatabaseSRID("2154")
    
    # ========= Databases management functions =========
    print("====== CREATING DATABASE ======")
    databaseTools.createDatabase("furbain")
    
    print("\n====== LIST DATABASES ======")
    projectList = databaseTools.getAllDatabasesProjects()
    print(projectList)
    
    print("\n====== SELECT DATABASE ======")
    databaseTools.selectDatabase("furbain")

    print("\n====== LIST TABLES ======")
    tables = databaseTools.getTablesFromDatabase()
    print(tables)
    
    print("====== DROP TABLE ======")
    databaseTools.deleteTable("vehicle")
    databaseTools.deleteTable("vehicleType")

    print("\n====== GET TABLE AS A DATAFRAME ======")
    gpdDf = databaseTools.getDatabaseTableDataframe("networkLink")
    print(gpdDf)
    
    print("\n====== CUSTOM SQL QUERY ======")
    results = databaseTools.executeSQLOnDatabase('SELECT * from "vehicleType"')
    
    
    # =====================================================================
    # ========================   DATABASE IMPORT   ========================
    # =====================================================================
    # Select the tables you want to import
    # => Import in the right order to avoid foreign key constraints problems
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
    
    # ========= IMPORT =========
    print("========== STARTING IMPORTATIONS ==========")
    for table in tablesToImport:
        launchImport(table)
    print(f"========== IMPORTED IN {str(datetime.now() - overallStartTime)[:-5]} ==========")
    
    
    # =====================================================================
    # ============================   QUERIES   ============================
    # =====================================================================
    
    # ========= Agents activities dataframes =========
    # Get dataframes of the activities of agents in each zone during given timespan
    allZonesDataframes = queries.agentActivity("./5zones.geojson", startTime='18:00:00', endTime='19:00:00', strictTime=False)
    for df in allZonesDataframes:
        print(df)
    
    
    # ========= OD Matrix =========
    # Get the OD matrix of trips between zones during given timespan
    # Generates csv files in "output" folder compatible with Arabesque http://arabesque.ifsttar.fr/  ->  https://github.com/gflowiz/arabesque
    finalODMatrix = queries.odMatrix("./5zones.geojson", startTime='14:30:00', endTime='15:00:00', ignoreArrivalTime=True, generateArabesqueFiles=True)
    for i in finalODMatrix:
        print('\t'.join(map(str, i)))
        
    # ========= Activity Sequences =========
    if __name__ == '__main__':
        resultDf = queries.activitySequences("./resources/sample/wholeCity.geojson", startTime='00:00:00', endTime='32:00:00', interval=15, createTableInDatabase=True, nbAgentsToProcess=200)
        


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