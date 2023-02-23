import sqlalchemy.types as types

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

DB_CONNECTION_STRING = 'postgresql+psycopg2://<username>:<password>@<location>:<port>/<databaseName>' # Connection string to the database (eg: postgresql+psycopg2://postgres:admin@localhost:5432/test)
DB_SRID = '2154' # SRID used in matsim
DB_USER = 'postgres'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost:5432'
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