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
    
    # Creating the tables in the database
    _createVehicleTypeTable()
    _createVehicleTable()
        
    # Importing the data to the database
    conn = tools.connectToDatabase()
    
    vehicleTypes.to_sql(config.DB_ALLVEHICLES_TYPES_TABLE, con=conn, if_exists='append', index=False)
    vehicles.to_sql(config.DB_ALLVEHICLES_TABLE, con=conn, if_exists='append', index=False)
    conn.close()


def _createVehicleTypeTable():
    conn = tools.connectToDatabase()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "vehicleType" (
            id character varying(50) NOT NULL,
            seats integer,
            "standingRoomInPersons" integer,
            length real,
            width real,
            "costInformation" character varying(50),
            "passengerCarEquivalents" real,
            "networkMode" character varying(50),
            "flowEfficiencyFactor" real,
            "accessTimeInSecondsPerPerson" real,
            "doorOperationMode" character varying(50),
            "egressTimeInSecondsPerPerson" real,
            PRIMARY KEY(id)
        );
    """)
    conn.close()


def _createVehicleTable():
    conn = tools.connectToDatabase()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS "vehicle" (
            id character varying(50) NOT NULL,
            "vehicleTypeId" character varying(50) NOT NULL,
            PRIMARY KEY(id),
            CONSTRAINT "vehicle_vehicleTypeId_fkey" 
                FOREIGN KEY("vehicleTypeId") 
                    REFERENCES "vehicleType"(id)
        );
    """)
    conn.close()