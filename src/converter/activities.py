import matsim.Plans as Plans
from furbain import config
from furbain import tools
from furbain import databaseTools
import pandas as pd
from geoalchemy2 import Geometry


def importActivities():
    plansDataframes = Plans.plan_reader_dataframe(experienced_plans_filepath=config.getExperiencedPlansPath(), plans_filepath=config.getPlansPath(), facilities_file_path=config.getFacilitiesPath())
    activitiesDataframe = plansDataframes.activities
    plans = plansDataframes.plans
    
    # Correcting start_time and end_time format
    activitiesDataframe['start_time'] = activitiesDataframe['start_time'].apply(lambda x: tools.formatTimeToIntervalType(x))
    activitiesDataframe['end_time'] = activitiesDataframe['end_time'].apply(lambda x: tools.formatTimeToIntervalType(x))
    
    # Creating a point from coordinates
    activitiesDataframe['location'] = activitiesDataframe.apply(lambda row: 'POINT({} {})'.format(row['x'], row['y']), axis=1)
    
    # associating the activities to the persons in the plans
    plans.rename(columns={'id':'plan_id'}, inplace=True)
    activitiesDataframe = pd.merge(activitiesDataframe, plans, on=['plan_id'], how='left')
    
    # Renaming the columns to match the database
    activitiesDataframe.rename(columns={
        'link': 'linkId',
        'facility': 'facilityId',
        'person_id': 'personId',
    }, inplace = True)
    
    # removing unused columns
    activitiesDataframe.drop(columns=['x', 'y', 'plan_id', 'score', 'selected'], inplace=True)
    
    # Creating the tables in the database
    _createActivityTable()
    
    # Importing the data to the database
    conn = databaseTools.connectToDatabase()
    activitiesDataframe.to_sql(config.DB_PLANS_TABLE, con=conn, if_exists='append', index=False, dtype={'location': Geometry('POINT', srid=config.getDatabaseSRID())})
    conn.close()


def _createActivityTable():
    conn = databaseTools.connectToDatabase()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_PLANS_TABLE}" (
            id integer NOT NULL,
            type character varying(40) COLLATE pg_catalog."default",
            location geometry,
            z numeric(40,20),
            start_time interval,
            end_time interval,
            max_dur interval,
            "typeBeforeCutting" character varying(40) COLLATE pg_catalog."default",
            "linkId" character varying(40) COLLATE pg_catalog."default",
            "facilityId" character varying(40) COLLATE pg_catalog."default",
            "personId" integer,
            CONSTRAINT activity_pkey PRIMARY KEY (id),
            CONSTRAINT "activity_facilityId_fkey" FOREIGN KEY ("facilityId")
                REFERENCES public.{config.DB_FACILITIES_TABLE} (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION,
            CONSTRAINT "activity_linkId_fkey" FOREIGN KEY ("linkId")
                REFERENCES public."{config.DB_NETWORK_TABLE}" (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION,
            CONSTRAINT "activity_personId_fkey" FOREIGN KEY ("personId")
                REFERENCES public.{config.DB_PERSONS_TABLE} (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE NO ACTION
        );
    """)
    conn.close()