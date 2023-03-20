import matsim.Vehicle as Vehicle
from furbain import config
from furbain import databaseTools

def importVehicles():
    vehicleDataframes = Vehicle.vehicle_reader(config.getAllVehiclesPath())
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
    conn = databaseTools.connectToDatabase()
    
    vehicleTypes.to_sql(config.DB_ALLVEHICLES_TYPES_TABLE, con=conn, if_exists='append', index=False)
    vehicles.to_sql(config.DB_ALLVEHICLES_TABLE, con=conn, if_exists='append', index=False)
    conn.close()


def _createVehicleTypeTable():
    conn = databaseTools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_ALLVEHICLES_TYPES_TABLE}" (
            id character varying(50) COLLATE pg_catalog."default" NOT NULL,
            seats integer,
            "standingRoomInPersons" integer,
            length real,
            width real,
            "costInformation" character varying(50) COLLATE pg_catalog."default",
            "passengerCarEquivalents" real,
            "networkMode" character varying(50) COLLATE pg_catalog."default",
            "flowEfficiencyFactor" real,
            "accessTimeInSecondsPerPerson" real,
            "doorOperationMode" character varying(50) COLLATE pg_catalog."default",
            "egressTimeInSecondsPerPerson" real,
            CONSTRAINT "vehicleType_pkey" PRIMARY KEY (id)
        );
    """)
    conn.close()


def _createVehicleTable():
    conn = databaseTools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_ALLVEHICLES_TABLE}" (
            id character varying(50) COLLATE pg_catalog."default" NOT NULL,
            "vehicleTypeId" character varying(50) COLLATE pg_catalog."default" NOT NULL,
            CONSTRAINT vehicle_pkey PRIMARY KEY (id),
            CONSTRAINT "vehicle_vehicleTypeId_fkey" FOREIGN KEY ("vehicleTypeId")
                REFERENCES public."{config.DB_ALLVEHICLES_TYPES_TABLE}" (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
        );
    """)
    conn.close()