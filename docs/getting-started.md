# Getting-started

___

## First thing to do

Here's a step-by-step tutorial on how to clone the GitHub repository of [matsim-output-postgreSQL-converter](https://github.com/gabRpt/matsim-output-postgreSQL-converter) to your local machine using git:

1. Install git on your machine if you haven't already.  
    => If you don't know what git is, here is a [guide](https://github.com/git-guides)  
    => If you just want to install it, check [here](https://github.com/git-guides/install-git)

2. Open your terminal or command prompt and navigate to the directory where you want to clone the repository.

3. Type the command `git clone https://github.com/gabRpt/matsim-output-postgreSQL-converter.git` and press Enter.

4. Wait for the cloning process to complete. This may take a few minutes depending on the size of the repository.

5. Once the cloning process is complete, you should see a new directory named `matsim-output-postgreSQL-converter` in the directory where you cloned the repository.

___

## Setup the database

#### Step 1: Install PostgreSQL with postGIS extension
*** If you already have PostgreSQL installed, go to the point n°3 ***

1. Go to the official PostgreSQL website (https://www.postgresql.org/) and download the PostgreSQL installer for your operating system.

2. Run the installer and follow the installation wizard to complete the installation process. Make sure to select the option to install postGIS extension during the installation process.

3. Once the installation is complete, open the PostgreSQL Stack Builder, which should have been installed along with PostgreSQL.

4. In the Stack Builder, select the version of PostgreSQL that you installed and click "Next".

5. In the "Select Categories" window, expand the "Spatial Extensions" category and select "postGIS" and any other  extensions you want to install.

6. Click "Next" and follow the instructions to complete the installation of postGIS extension.

#### Step 2: Set up the binary paths in pgAdmin4

1. If you don't have pgAdmin4 installed, download and install it from the official pgAdmin website (https://www.pgadmin.org/).

2. Open pgAdmin4 and go to "File" > "Preferences" > "Paths".

3. In the "Binary paths" tab, scroll down to "PostgreSQL Binary Path" and click add the binary path in the field corresponding to the version of PostgreSQL you installed.

4. Browse to the directory where PostgreSQL is installed (e.g. C:\Program Files\PostgreSQL\14\bin) and select it.

5. Click "Select" to save the path.

#### Step 3: Create a database with a backup file

1. In pgAdmin4, on the left panel, right-click on "Databases" and select "Create" > "Database".

2. In the "Create - Database" window, enter a name for the new database and leave the other options at their default values.

3. Click "Save" to create the database.

4. Right-click on the new database and select "Restore...".

5. In the "Restore" window, select "Custom or tar" as the format and click in the field below to browse for the backup file.

6. Navigate to the directory where the backup file is located (./resources/setup/[databaseBackupPostgresCustom](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/setup/databaseBackupPostgresCustom "databaseBackupPostgresCustom")) and select the backup file.

7. Click "Restore" to restore the database from the backup file.

___

## Setup the environment

*** For this part, I am using Anaconda ***
1. Install `Anaconda` on your machine. You can follow the instructions in this [guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). Direct download [here](https://www.anaconda.com/products/distribution).

2. Open Anaconda Navigator and navigate to the "Environments" tab in the left panel.

3. Click on the "Import" button and select the matsimConverterEnv.yaml file located in the ./resources/setup/ folder of the cloned repository.

4. Give a name to your new environment and wait for the setup process to complete.

5. Once the environment is created, **select it** and launch an IDE like VS Code from Anaconda Navigator.

6. Open a terminal in the IDE and run the command `pip install ./resources/setup/matsim_tools-1.0.5-py3-none-any.whl` to install the required matsim_tools package. **Please verify that you are installing the lastest version available in ./resources/setup/**

___

## Configuration

In [config.py](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/src/config.py "config.py") file, edit the commented constants
* PATH_SIMULATION_OUTPUT
* DB_CONNECTION_STRING
* DB_SRID