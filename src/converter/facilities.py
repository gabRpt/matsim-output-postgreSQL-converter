import matsim.Facility as Facility
from furbain import config
from furbain import databaseTools
import geopandas as gpd
from geoalchemy2 import Geometry

def importFacilities():
    facilityReader = Facility.facility_reader(config.PATH_FACILITIES)
    facilities = gpd.GeoDataFrame(facilityReader.facilities)
    
    # Renaming the columns to match the database
    facilities.rename(columns={
        'type': 'activityType'
    }, inplace = True)
    
    
    # Creating a point from coordinates
    facilities['location'] = facilities.apply(lambda row: 'POINT({} {})'.format(row['x'], row['y']), axis=1)
    facilities.drop(columns=['x', 'y'], inplace=True)
    
    # Creating the tables in the database
    _createFacilityTable()
    
    # Importing the data to the database
    conn = databaseTools.connectToDatabase()
    facilities.to_sql(config.DB_FACILITIES_TABLE, con=conn, if_exists='append', index=False, dtype={'location': Geometry('POINT', srid=config.getDatabaseSRID())})
    conn.close()

def _createFacilityTable():
    conn = databaseTools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_FACILITIES_TABLE}" (
            id character varying(40) COLLATE pg_catalog."default" NOT NULL,
            "linkId" character varying(40) COLLATE pg_catalog."default",
            location geometry,
            "activityType" character varying(40) COLLATE pg_catalog."default",
            CONSTRAINT facility_pkey PRIMARY KEY (id),
            CONSTRAINT "facility_linkId_fkey" FOREIGN KEY ("linkId")
                REFERENCES public."{config.DB_NETWORK_TABLE}" (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
        );
    """)
    conn.close()