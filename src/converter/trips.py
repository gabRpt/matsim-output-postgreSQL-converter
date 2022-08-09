import config
import tools
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
    tripsDataframe['dep_time'] = tripsDataframe['dep_time'].apply(lambda x: tools.checkAndCorrectTime(x))
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    tripsDataframe.to_sql(config.DB_TRIPS_TABLE, con=conn, if_exists='append', index=False)
    conn.close()