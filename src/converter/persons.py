import config
import tools
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
        
    # Importing the data to the database
    conn = tools.connectToDatabase()
    personGeoDataframe.to_sql(config.DB_PERSONS_TABLE, con=conn, if_exists='append', index=False, dtype={'first_act_coord': Geometry('POINT', srid=config.DB_SRID)})
