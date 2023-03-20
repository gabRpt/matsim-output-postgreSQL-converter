import sqlalchemy.types as types
import pathlib
import json
from os.path import isdir

DB_DBNAME = ''

# Names of the tables in the database
DB_ALLVEHICLES_TABLE = 'vehicle' 
DB_ALLVEHICLES_TYPES_TABLE = 'vehicleType'
DB_EVENTS_TABLE = 'networkLinkTraffic'
DB_FACILITIES_TABLE = 'facility'
DB_HOUSEHOLDS_TABLE = 'household'
DB_NETWORK_TABLE = 'networkLink'
DB_PERSONS_TABLE = 'person'
DB_PLANS_TABLE = 'activity'
DB_TRIPS_TABLE = 'trip'
DB_BUILDINGS_TABLE = 'building'

# Separators for the csv files
PERSONS_CSV_SEPARATOR = ';'
TRIPS_CSV_SEPARATOR = ';'
DETAILED_NETWORK_CSV_SEPARATOR = ','


# ===== QUERIES =====
ARABESQUE_DEFAULT_SRID = '4326' # EPSG used by Arabesque
ARABESQUE_GENERATED_FILES_DIRECTORY_PATH = './output/'

ACTIVITY_SEQUENCES_TABLE_NAME = 'activitySequences'
ACTIVITY_SEQUENCES_TABLE_TIME_FORMAT = '%d_%m_%Y_%H_%M_%S' # time used to indicate when the table was generated, it will be added to the table name
ACTIVITY_SEQUENCES_TABLE_COLUMNS = {
    "id": types.Integer,
    "personId": types.Integer,
    "periodStart": types.Interval,
    "periodEnd": types.Interval,
    "mainActivityId": types.Integer,
    "startActivityId": types.Integer,
    "endActivityId": types.Integer,
    "mainActivityStartTime": types.Interval,
    "mainActivityEndTime": types.Interval,
    "timeSpentInMainActivity": types.Interval
}
ACTIVITY_SEQUENCES_DB_PROGRESS_BAR_PERCENTAGE = 5 # the progress bar will be updated every 10% of the table


# ===== CONFIGURATION ENV =====
PATH_CONFIGURATION_FILE = pathlib.Path.home() / '.furbain' / 'config.json'


def createConfigurationFile():
    # Create the config file if it doesn't exist
    fileToCreate = PATH_CONFIGURATION_FILE
    
    if not fileToCreate.exists():
        fileToCreate.parent.mkdir(parents=True, exist_ok=True)
        fileToCreate.touch()
        fileToCreate.write_text("""{
    "db_host": "localhost",
    "db_port": "5432",
    "db_user": "postgres",
    "db_password": "postgres",
    "db_srid": "2154",
    "path_simulation_output": "C:/Users/name/Documents/matsimOutput/simulation_output",
    "allvehicles_filename": "output_allvehicles.xml.gz",
    "events_filename": "output_events.xml.gz",
    "facilities_filename": "output_facilities.xml.gz",
    "households_filename": "output_households.xml.gz",
    "legs_filename": "output_legs.csv.gz",
    "network_filename": "output_network.xml.gz",
    "persons_filename": "output_persons.csv.gz",
    "plans_filename": "output_plans.xml.gz",
    "experienced_plans_filename": "output_experienced_plans.xml.gz",
    "trips_filename": "output_trips.csv.gz",
    "detailed_network_filename": "detailed_network.csv",
    "buildings_filename": "BUILDINGS.geojson"
}""")

def loadConfigurationFile():
    fileToLoad = PATH_CONFIGURATION_FILE

    if not fileToLoad.exists():
        createConfigurationFile()
    
    with open(fileToLoad) as json_file:
        return json.load(json_file)


def saveConfigurationFile(config):
    fileToSave = PATH_CONFIGURATION_FILE

    if not fileToSave.exists():
        createConfigurationFile()
    
    with open(fileToSave, 'w') as outfile:
        json.dump(config, outfile, indent=4)


def setVariableInConfigurationFile(name, value):
    config = loadConfigurationFile()
    config[name] = value
    saveConfigurationFile(config)

def getVariableInConfigurationFile(name):
    config = loadConfigurationFile()
    return config[name]

# ----- User -----
def setDatabaseUser(user):    
    setVariableInConfigurationFile('db_user', user)

def getDatabaseUser():
    return getVariableInConfigurationFile('db_user')


# ----- Password -----
def setDatabasePassword(password):
    setVariableInConfigurationFile('db_password', password)

def getDatabasePassword():
    return getVariableInConfigurationFile('db_password')


# ----- Host -----
def setDatabaseHost(host):
    setVariableInConfigurationFile('db_host', host)

def getDatabaseHost():
    return getVariableInConfigurationFile('db_host')


# ----- Port -----
def setDatabasePort(port):
    setVariableInConfigurationFile('db_port', port)

def getDatabasePort():
    return getVariableInConfigurationFile('db_port')


# ----- Database SRID -----
def setDatabaseSRID(srid):
    setVariableInConfigurationFile('db_srid', srid)

def getDatabaseSRID():
    return getVariableInConfigurationFile('db_srid')


# ----- Simulation output paths -----
def setSimulationOutputPath(path):
    # Add '/' at the end if it doesn't exist
    if path[-1] != '/':
        path += '/'
    
    # Check if the path exists
    if not isdir(path):
        raise Exception('The path ' + path + ' doesn\'t exist')
    
    setVariableInConfigurationFile('path_simulation_output', path)

def getSimulationOutputPath():
    return getVariableInConfigurationFile('path_simulation_output')


# ----- Output files paths -----
def getAllVehiclesPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('allvehicles_filename')

def getEventsPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('events_filename')

def getFacilitiesPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('facilities_filename')

def getHouseholdsPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('households_filename')

def getLegsPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('legs_filename')

def getNetworkPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('network_filename')

def getPersonsPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('persons_filename')

def getPlansPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('plans_filename')

def getExperiencedPlansPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('experienced_plans_filename')

def getTripsPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('trips_filename')

def getDetailedNetworkPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('detailed_network_filename')

def getBuildingsPath():
    return getSimulationOutputPath() + getVariableInConfigurationFile('buildings_filename')