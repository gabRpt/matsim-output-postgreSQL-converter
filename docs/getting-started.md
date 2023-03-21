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

* If you don't have pgAdmin4 installed, download and install it from the official pgAdmin website (https://www.pgadmin.org/).

{% method %}
* Open pgAdmin4 and go to "File" > "Preferences" > "Paths".

* In the "Binary paths" tab, scroll down to "PostgreSQL Binary Path" and click add the binary path in the field corresponding to the version of PostgreSQL you installed.

* Browse to the directory where PostgreSQL is installed (e.g. C:\Program Files\PostgreSQL\14\bin) and select it.

* Click "Select" to save the path.
{% common %}
![Postgre setup binary path](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/getting-started/postgre_binay_path.png)

{% endmethod %}

#### Step 3: Create a database

{% method %}

* In pgAdmin4, on the left panel, right-click on "Databases" and select "Create" > "Database".
{% common %}
![Postgre create database](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/getting-started/postgre_create_db_1.png)

{% endmethod %}
{% method %}

* In the "Create - Database" window, enter a name for the new database and leave the other options at their default values.

* Click "Save" to create the database.
{% common %}
![Postgre create database](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/getting-started/postgre_create_db_2.png)

{% endmethod %}

___

## Setup the environment

***For this part, I am using Anaconda***

* Install `Anaconda` on your machine. You can follow the instructions in this [guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). Direct download [here](https://www.anaconda.com/products/distribution).

{% method %}

* Open Anaconda Navigator and navigate to the `Environments` tab in the left panel.

* Click on the `Create` button and enter a name for the new environment.

{% common %}
![Anaconda create environment](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/getting-started/anaconda_create_env.png)
{% endmethod %}

{% method %}

* Give a name to your new environment and wait for the setup process to complete.

* Once the environment is created, **select it** and launch an IDE like VS Code from Anaconda Navigator.
{% common %}
![Anaconda select environment](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/getting-started/anaconda_select_env.png)

{% endmethod %}
{% method %}
TODO MODIFY PIP INSTALL

* Open a terminal in the IDE and run the command `pip install ./resources/setup/furbain-1.0.0-py3-none-any.whl` to install the required matsim_tools package. **Please verify that you are installing the lastest version available in ./resources/setup/**

{% endmethod %}