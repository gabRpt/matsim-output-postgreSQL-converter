from furbain import config
from furbain import tools
from furbain import databaseTools
import pandas as pd


def importTrips():
    tripsDataframe = pd.read_csv(config.PATH_TRIPS, sep=config.TRIPS_CSV_SEPARATOR)
    
    tripsDataframe.drop(columns=[
        'start_activity_type',
        'end_activity_type',
        'start_x',
        'start_y',
        'end_x',
        'end_y',
    ], inplace=True)
    
    # Renaming the columns to match the database
    tripsDataframe.rename(columns={
        'trip_id': 'id',
        'person': 'personId',
    }, inplace = True)
    
    # Correcting dep_time format
    tripsDataframe['dep_time'] = tripsDataframe['dep_time'].apply(lambda x: tools.formatTimeToIntervalType(x))
    
    # Creating the tables in the database
    _createTripTable()
    
    # Importing the data to the database
    conn = databaseTools.connectToDatabase()
    tripsDataframe.to_sql(config.DB_TRIPS_TABLE, con=conn, if_exists='append', index=False)
    conn.close()

def _createTripTable():
    conn = databaseTools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_TRIPS_TABLE}" (
            id character varying(40) COLLATE pg_catalog."default" NOT NULL,
            "personId" integer,
            trip_number integer,
            dep_time interval,
            trav_time interval,
            wait_time interval,
            traveled_distance integer,
            euclidean_distance integer,
            main_mode character varying(40) COLLATE pg_catalog."default",
            longest_distance_mode character varying(40) COLLATE pg_catalog."default",
            modes character varying(40) COLLATE pg_catalog."default",
            start_facility_id character varying(40) COLLATE pg_catalog."default",
            start_link character varying(40) COLLATE pg_catalog."default",
            end_facility_id character varying(40) COLLATE pg_catalog."default",
            end_link character varying(40) COLLATE pg_catalog."default",
            first_pt_boarding_stop character varying(40) COLLATE pg_catalog."default",
            last_pt_egress_stop character varying(40) COLLATE pg_catalog."default",
            CONSTRAINT trip_pkey PRIMARY KEY (id),
            CONSTRAINT trip_end_facility_id_fkey FOREIGN KEY (end_facility_id)
                REFERENCES public.{config.DB_FACILITIES_TABLE} (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION,
            CONSTRAINT trip_end_link_fkey FOREIGN KEY (end_link)
                REFERENCES public."{config.DB_NETWORK_TABLE}" (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION,
            CONSTRAINT "trip_personId_fkey" FOREIGN KEY ("personId")
                REFERENCES public.{config.DB_PERSONS_TABLE} (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION,
            CONSTRAINT trip_start_facility_id_fkey FOREIGN KEY (start_facility_id)
                REFERENCES public.{config.DB_FACILITIES_TABLE} (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION,
            CONSTRAINT trip_start_link_fkey FOREIGN KEY (start_link)
                REFERENCES public."{config.DB_NETWORK_TABLE}" (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
        );
    """)
    conn.close()