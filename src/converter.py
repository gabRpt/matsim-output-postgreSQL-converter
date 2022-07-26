import matsim
import config
import tools
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry

def importVehicles():
    vehicleDataframes = matsim.Vehicle.vehicle_reader(config.PATH_ALLVEHICLE)
    vehicleTypes = vehicleDataframes.vehicle_types
    vehicles = vehicleDataframes.vehicles
    
    # Renamming the columns to match the database
    vehicleTypes.rename(columns={
        'pce':'passengerCarEquivalents',
        'factor': 'flowEfficiencyFactor'
    }, inplace = True)
    
    vehicles.rename(columns={
        'type': 'vehicleTypeId'
    }, inplace = True)
    
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    vehicleTypes.to_sql('vehicleType', con=conn, if_exists='append', index=False)
    vehicles.to_sql('vehicle', con=conn, if_exists='append', index=False)


def importHouseholds():
    householdReader = matsim.Household.houshold_reader(config.PATH_HOUSEHOLDS)
    householdDataframe = householdReader.households
    
    # Formating dataframe
    householdDataframe.drop(columns=['members'], inplace=True)
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    householdDataframe.to_sql('household', con=conn, if_exists='append', index=False)


def importPersons():
    personsDataframe = pd.read_csv(config.PATH_PERSONS, sep=';')
    personGeoDataframe = gpd.GeoDataFrame(personsDataframe)
    
    # Renaming the columns to match the database
    personGeoDataframe.rename(columns={
        'person': 'id',
    }, inplace = True)
    
    # Creating a point from first activity coordinates
    personGeoDataframe['first_act_point'] = personGeoDataframe.apply(lambda row: 'POINT({} {})'.format(row['first_act_x'], row['first_act_y']), axis=1)
    personGeoDataframe.drop(columns=['first_act_x', 'first_act_y'], inplace=True)
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    personGeoDataframe.to_sql('person', con=conn, if_exists='append', index=False, dtype={'first_act_coord': Geometry('POINT', srid=config.DB_SRID)})


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