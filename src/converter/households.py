import matsim.Household as Household
from furbain import config
from furbain import tools

def importHouseholds():
    householdReader = Household.houshold_reader(config.PATH_HOUSEHOLDS)
    householdDataframe = householdReader.households
    
    # Formating dataframe
    householdDataframe.drop(columns=['members'], inplace=True)
    
    # Creating the tables in the database
    _createHouseholdTable()
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    householdDataframe.to_sql(config.DB_HOUSEHOLDS_TABLE, con=conn, if_exists='append', index=False)
    conn.close()


def _createHouseholdTable():
    conn = tools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_HOUSEHOLDS_TABLE}" (
            id integer NOT NULL,
            "bikeAvailability" character varying COLLATE pg_catalog."default",
            "carAvailability" character varying COLLATE pg_catalog."default",
            "censusId" integer,
            household_income numeric(40,20),
            CONSTRAINT household_pkey PRIMARY KEY (id)
        );
    """)
    conn.close()