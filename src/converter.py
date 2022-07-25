import matsim
import config
import tools
import pandas as pd

def importVehicles():
    vehicle_dataframes = matsim.Vehicle.vehicle_reader(config.PATH_ALLVEHICLE)
    vehicle_types = vehicle_dataframes.vehicle_types
    vehicles = vehicle_dataframes.vehicles
    
    # Renamming the columns to match the database
    vehicle_types.rename(columns={
        'pce':'passengerCarEquivalents',
        'factor': 'flowEfficiencyFactor'
    }, inplace = True)
    
    vehicles.rename(columns={
        'type': 'vehicleTypeId'
    }, inplace = True)
    
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    vehicle_types.to_sql('vehicleType', con=conn, if_exists='append', index=False)
    vehicles.to_sql('vehicle', con=conn, if_exists='append', index=False)


def importHouseholds():
    household_reader = matsim.Household.houshold_reader(config.PATH_HOUSEHOLDS)
    household_dataframe = household_reader.households
    
    # Formating dataframe
    household_dataframe.drop(columns=['members'], inplace=True)
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    household_dataframe.to_sql('household', con=conn, if_exists='append', index=False)


def importPersons():
    pass

def importNetworkLinks():
    pass

def importFacilities():
    pass

def importTrips():
    pass

def importActivities():
    pass

def importEvents():
    pass