from datetime import datetime
import queries
import converter

def main():
    overallStartTime = datetime.now()
    
    
    # =====================================================================
    # ========================   DATABASE IMPORT   ========================
    # =====================================================================
    
    # Select the tables you want to import
    # => Import in the right order to avoid foreign key constraints problems
    tablesToImport = [
        # "vehicles",
        # "households",
        # "persons",
        # "networkLinks",
        # "facilities",
        # "trips",
        # "activities",
        # "events",
        # "buildings",
    ]
    
    # ========= IMPORT =========
    # print("========== STARTING IMPORTATIONS ==========")
    # for table in tablesToImport:
    #     launchImport(table)
    # print(f"========== IMPORTED IN {str(datetime.now() - overallStartTime)[:-5]} ==========")
    
    
    
    
    # =====================================================================
    # ============================   QUERIES   ============================
    # =====================================================================
    
    # ========= Agents activities dataframes =========
    # # Get dataframes of the activities of agents in each zone during given timespan
    allZonesDataframes = queries.agentActivity.agentActivity("./resources/sample/5zones.geojson", startTime='18:00:00', endTime='19:00:00', strictTime=False)
    print(allZonesDataframes)
    
    
    
    # ========= OD Matrix =========
    # # Get the OD matrix of trips between zones during given timespan
    # # Generates csv files in "output" folder compatible with Arabesque http://arabesque.ifsttar.fr/  ->  https://github.com/gflowiz/arabesque
    # finalODMatrix = queries.odMatrix.odMatrix("./resources/sample/5zones.geojson", startTime='14:30:00', endTime='15:00:00', ignoreArrivalTime=True, generateArabesqueFiles=True)
    
    # for i in finalODMatrix:
        # print('\t'.join(map(str, i)))
        
    
    
    # ========= Activity Sequences =========
    # if __name__ == '__main__':
        # resultDf = queries.activitySequences.activitySequences("./resources/sample/wholeCity.geojson", startTime='00:00:00', endTime='32:00:00', interval=15, createTableInDatabase=True, nbAgentsToProcess=200)
        


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