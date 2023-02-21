import matsim.Household as Household
from furbain import config
from furbain import tools

def importHouseholds():
    householdReader = Household.houshold_reader(config.PATH_HOUSEHOLDS)
    householdDataframe = householdReader.households
    
    # Formating dataframe
    householdDataframe.drop(columns=['members'], inplace=True)
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    householdDataframe.to_sql(config.DB_HOUSEHOLDS_TABLE, con=conn, if_exists='append', index=False)
    conn.close()