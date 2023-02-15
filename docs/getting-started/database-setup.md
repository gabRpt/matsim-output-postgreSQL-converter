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