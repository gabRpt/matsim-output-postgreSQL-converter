import matsim.Vehicle as Vehicle
from furbain import config
from furbain import tools

def importVehicles():
    vehicleDataframes = Vehicle.vehicle_reader(config.PATH_ALLVEHICLES)
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
    vehicleTypes.to_sql(config.DB_ALLVEHICLES_TYPES_TABLE, con=conn, if_exists='append', index=False)
    vehicles.to_sql(config.DB_ALLVEHICLES_TABLE, con=conn, if_exists='append', index=False)
    conn.close()