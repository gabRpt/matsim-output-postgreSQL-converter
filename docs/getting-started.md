# Getting-started

___

## Installation
#### Setup the database
* Install [postgeSQL](https://www.postgresql.org/) database with [postGIS extension](https://postgis.net/) using postgreSQL Stack Builder
* If using pgAdmin4, setup the binary paths. File > Preferences > Paths > Binary paths > PostgreSQL Binary Path
* Create a new database
	* Right click on the created database > restore
	* Format : Custom
	* Filename : select the file located in ./resources/setup/[databaseBackupPostgresCustom](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/setup/databaseBackupPostgresCustom "databaseBackupPostgresCustom")

#### Setup the environment
* `git clone https://github.com/gabRpt/matsim-output-postgreSQL-converter.git` 
* Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Anaconda recommended)
* In environments tab, create a new environment by importing [matsimConverterEnv.yaml](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/setup/matsimConverterEnv.yaml "matsimConverterEnv.yaml")
* Launch an IDE like VS Code from Anaconda Navigator
* `pip install ./resources/setup/matsim_tools-1.0.3-py3-none-any.whl`


___


## Configuration
In [config.py](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/src/config.py "config.py") file, edit the commented constants
* PATH_SIMULATION_OUTPUT
* DB_CONNECTION_STRING
* DB_SRID
