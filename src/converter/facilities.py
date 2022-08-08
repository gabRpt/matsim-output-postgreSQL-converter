import matsim.Facility as Facility
import config
import tools
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
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    facilities.to_sql('facility', con=conn, if_exists='append', index=False, dtype={'location': Geometry('POINT', srid=config.DB_SRID)})
