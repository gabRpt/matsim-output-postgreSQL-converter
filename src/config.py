import sqlalchemy.types as types
import pathlib
import json

# Path to the simulation output folder like on windows don't use backslash '\' and replace them with normal slash '/'
PATH_SIMULATION_OUTPUT = 'C:/Users/name/Documents/matsimOutput/simulation_output'

PATH_ALLVEHICLES = PATH_SIMULATION_OUTPUT + '/output_allvehicles.xml.gz'
PATH_EVENTS = PATH_SIMULATION_OUTPUT + '/output_events.xml.gz'
PATH_FACILITIES = PATH_SIMULATION_OUTPUT + '/output_facilities.xml.gz'
PATH_HOUSEHOLDS = PATH_SIMULATION_OUTPUT + '/output_households.xml.gz'
PATH_LEGS = PATH_SIMULATION_OUTPUT + '/output_legs.csv.gz'
PATH_NETWORK = PATH_SIMULATION_OUTPUT + '/output_network.xml.gz'
PATH_PERSONS = PATH_SIMULATION_OUTPUT + '/output_persons.csv.gz'
PATH_PLANS = PATH_SIMULATION_OUTPUT + '/output_plans.xml.gz'
PATH_EXPERIENCED_PLANS = PATH_SIMULATION_OUTPUT + '/output_experienced_plans.xml.gz'
PATH_TRIPS = PATH_SIMULATION_OUTPUT + '/output_trips.csv.gz'
PATH_DETAILED_NETWORK = PATH_SIMULATION_OUTPUT + '/detailed_network.csv'
PATH_BUILDINGS = PATH_SIMULATION_OUTPUT + '/BUILDINGS.geojson'

DB_SRID = '2154' # SRID used in matsim
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

# ----- User -----
def setDatabaseUser(user):
    config = loadConfigurationFile()
    config['db_user'] = user
    saveConfigurationFile(config)

def getDatabaseUser():
    config = loadConfigurationFile()
    return config['db_user']

# ----- Password -----
def setDatabasePassword(password):
    config = loadConfigurationFile()
    config['db_password'] = password
    saveConfigurationFile(config)

def getDatabasePassword():
    config = loadConfigurationFile()
    return config['db_password']

# ----- Host -----
def setDatabaseHost(host):
    config = loadConfigurationFile()
    config['db_host'] = host
    saveConfigurationFile(config)

def getDatabaseHost():
    config = loadConfigurationFile()
    return config['db_host']

# ----- Port -----
def setDatabasePort(port):
    config = loadConfigurationFile()
    config['db_port'] = port
    saveConfigurationFile(config)

def getDatabasePort():
    config = loadConfigurationFile()
    return config['db_port']