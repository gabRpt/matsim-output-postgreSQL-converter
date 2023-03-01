from furbain import config
from furbain import tools
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry


def importPersons():
    personsDataframe = pd.read_csv(config.PATH_PERSONS, sep=config.PERSONS_CSV_SEPARATOR)
    personGeoDataframe = gpd.GeoDataFrame(personsDataframe)
    
    # Renaming the columns to match the database
    personGeoDataframe.rename(columns={
        'person': 'id',
    }, inplace = True)
    
    # Creating a point from first activity coordinates
    personGeoDataframe['first_act_point'] = personGeoDataframe.apply(lambda row: 'POINT({} {})'.format(row['first_act_x'], row['first_act_y']), axis=1)
    personGeoDataframe.drop(columns=['first_act_x', 'first_act_y'], inplace=True)
    
    # Creating the tables in the database
    _createPersonTable()
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    personGeoDataframe.to_sql(config.DB_PERSONS_TABLE, con=conn, if_exists='append', index=False, dtype={'first_act_coord': Geometry('POINT', srid=config.DB_SRID)})
    conn.close()

def _createPersonTable():
    conn = tools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_PERSONS_TABLE}" (
            id integer NOT NULL,
            executed_score numeric(40,20),
            first_act_type character varying(50) COLLATE pg_catalog."default",
            "htsPersonId" integer,
            sex "char",
            "bikeAvailability" character varying(50) COLLATE pg_catalog."default",
            "htsHouseholdId" integer,
            "censusPersonId" integer,
            employed boolean,
            "motorbikesAvailability" character varying(50) COLLATE pg_catalog."default",
            "householdId" integer,
            "hasLicense" boolean,
            "carAvailability" character varying(50) COLLATE pg_catalog."default",
            "hasPtSubscription" boolean,
            "isPassenger" boolean,
            age smallint,
            "householdIncome" numeric(40,20),
            "censusHouseholdId" integer,
            "isOutside" boolean,
            first_act_point geometry,
            CONSTRAINT person_pkey PRIMARY KEY (id),
            CONSTRAINT "person_householdId_fkey" FOREIGN KEY ("householdId")
                REFERENCES public.{config.DB_HOUSEHOLDS_TABLE} (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
        );
    """)
    conn.close()