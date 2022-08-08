PATH_SIMULATION_OUTPUT = 'C:/Users/name/Documents/matsimOutput/simulation_output' # Path to the simulation output folder like

PATH_ALLVEHICLE = PATH_SIMULATION_OUTPUT + '/output_allvehicles.xml.gz'
PATH_EVENTS = PATH_SIMULATION_OUTPUT + '/output_events.xml.gz'
PATH_EXPERIENCED_PLANS = PATH_SIMULATION_OUTPUT + '/output_experienced_plans.xml.gz'
PATH_FACILITIES = PATH_SIMULATION_OUTPUT + '/output_facilities.xml.gz'
PATH_HOUSEHOLDS = PATH_SIMULATION_OUTPUT + '/output_households.xml.gz'
PATH_LEGS = PATH_SIMULATION_OUTPUT + '/output_legs.csv'
PATH_NETWORK = PATH_SIMULATION_OUTPUT + '/output_network.xml.gz'
PATH_PERSONS = PATH_SIMULATION_OUTPUT + '/output_persons.csv'
PATH_PLANS = PATH_SIMULATION_OUTPUT + '/output_plans.xml.gz'
PATH_TRIPS = PATH_SIMULATION_OUTPUT + '/output_trips.csv'
PATH_DETAILED_NETWORK = PATH_SIMULATION_OUTPUT + '/detailed_network.csv'

DB_CONNECTION_STRING = 'postgresql+psycopg2://<username>:<password>@<location>:<port>/<databaseName>' # Connection string to the database (eg: postgresql+psycopg2://postgres:admin@localhost:5432/test)
DB_SRID = '2154' # SRID used in matsim