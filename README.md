# matsim-output-postgreSQL-converter
Tool to convert matsim output to [postgeSQL](https://www.postgresql.org/) database with [postGIS extension](https://postgis.net/)

Using custom matsim-tools package [enriched project](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/matsim_tools-1.0.0-py3-none-any.whl) / [original project](https://github.com/matsim-vsp/matsim-python-tools)

# Database diagram
You can see the following diagram more in details at https://dbdiagram.io/d/62bc660c69be0b672c6841b3
![Diagram available at https://dbdiagram.io/d/62bc660c69be0b672c6841b3](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/database_diagram.png)


# How to start
## Setup the database
* Install [postgeSQL](https://www.postgresql.org/) database with [postGIS extension](https://postgis.net/) using postgreSQL Stack Builder
* If using pgAdmin4, setup the binary paths. File > Preferences > Paths > Binary paths > PostgreSQL Binary Path
* Create a new database
	* Right click on the created database > restore
	* Format : Custom
	* Filename : select the file located in ./resources/[databaseBackupPostgresCustom](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/databaseBackupPostgresCustom "databaseBackupPostgresCustom")


## Setup the environment
* `git clone https://github.com/gabRpt/matsim-output-postgreSQL-converter.git` 
* Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Anaconda recommended)
* In environments tab, create a new environment by importing [matsimConverterEnv.yaml](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/matsimConverterEnv.yaml "matsimConverterEnv.yaml")
* Launch an IDE like VS Code from Anaconda Navigator
* `pip install ./resources/matsim_tools-1.0.0-py3-none-any.whl`

## Setup the converter
* In [config.py](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/src/config.py "config.py") file setup edit the commented constant
	* PATH_SIMULATION_OUTPUT
	* DB_CONNECTION_STRING
	* DB_SRID
* In [main.py](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/src/main.py "main.py") edit the array indicating which tables will be imported
