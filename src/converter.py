from matsim import Vehicle
import config
import tools

def importVehicles():
    vehicle_dataframes = Vehicle.vehicle_reader(config.PATH_ALLVEHICLE)
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