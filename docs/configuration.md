# Configuration

___


## Introduction

Once you have opened your IDE, you can create a new python file and write `import furbain` and execute it. This will generate the configuration file.  

On windows, furbain's configuration file is located at `C:\Users\name\.furbain\config.json`.  
This file contains the database credentials and the path to the MATSim output files.  

To modifiy these informations you can either edit the file manually or use the following functions:

## Functions

### User

`setDatabaseUser(user)` : sets the database user. (string default: `postgres`)  
`getDatabaseUser()` : returns the database user.  


### Password

`setDatabasePassword(password)` : sets the database password. (string default: `postgres`)  
`getDatabasePassword()` : returns the database password.  


### Host

`setDatabaseHost(host)` : sets the database host. (string default: `localhost`)  
`getDatabaseHost()` : returns the database host.  

### Port

`setDatabasePort(port)` : sets the database port. (string default: `5432`)  
`getDatabasePort()` : returns the database port.  

### SRID

`setDatabaseSRID(srid)` : sets the database SRID. (string default: `4326`)  
`getDatabaseSRID()` : returns the database SRID.  

### Simulation output path

`setSimulationOutputPath(path)` : sets the path to the MATSim output files. (string default: `C:/Users/name/Documents/matsimOutput/simulation_output`)  
**On windows, do not use a backslash `\` but simple slash `/` in the path**  
`getSimulationOutputPath()` : returns the path to the MATSim output files.  

## Set or get a variable in the configuration file

`setVariableInConfigurationFile(name, value)` : sets a variable in the configuration file.  
`getVariableInConfigurationFile(name)` : returns a variable in the configuration file.  

Here are the variables you can set with their default values :

```json
{
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
}
```

Below `path_simulation_output` are the filenames of the output files of your simulation.
