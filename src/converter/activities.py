import matsim.Plans as Plans
import config
import tools
import pandas as pd
from geoalchemy2 import Geometry


def importActivities():
    plansDataframes = Plans.plan_reader_dataframe(experienced_plans_filepath=config.PATH_EXPERIENCED_PLANS, plans_filepath=config.PATH_PLANS)
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
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    activitiesDataframe.to_sql(config.DB_PLANS_TABLE, con=conn, if_exists='append', index=False, dtype={'location': Geometry('POINT', srid=config.DB_SRID)})
    conn.close()
