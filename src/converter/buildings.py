import collections
from furbain import config
from furbain import tools
import geopandas as gpd
import pandas as pd
import json
from geoalchemy2 import Geometry

def importBuildings():
    
    with open(config.PATH_BUILDINGS, 'r') as buildingsJson:
        buildings = json.load(buildingsJson)        
        polygonFeaturesDict = collections.defaultdict(list)
        
        for feature in buildings['features']:
            # Checking if the feature has coordinates
            if len(feature['geometry']['coordinates'][0]) == 0:
                continue
            
            # Checking supported geometry type
            if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
                polygonString = _convertCoordinatesToPolygon(feature['geometry']['coordinates'])
                
            else:
                print(f'WARNING: geometry type "{feature["geometry"]["type"]}" not supported. Skipping feature.')
                continue
        
            polygonFeaturesDict['geometryType'].append(feature['geometry']['type'])
            polygonFeaturesDict['type'].append(feature['type'])
            polygonFeaturesDict['PK'].append(feature['properties']['PK'])
            polygonFeaturesDict['height'].append(feature['properties']['HEIGHT'])         
            polygonFeaturesDict['geometry'].append(polygonString)
            
        polygonDataframe = pd.DataFrame(polygonFeaturesDict)
        
        # Creating the tables in the database
        _createBuildingTable()
        
        # Importing the data to the database        
        conn = tools.connectToDatabase()
        polygonDataframe.to_sql(config.DB_BUILDINGS_TABLE, con=conn, if_exists='append', index=False, dtype={'geom': Geometry('POLYGON', srid=config.getDatabaseSRID())})
        conn.close()


def _createBuildingTable():
    conn = tools.connectToDatabase()
    conn.execute(f"""
        CREATE SEQUENCE public.building_id_seq
            START WITH 1
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1;
    """)
    
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS "{config.DB_BUILDINGS_TABLE}" (
            id bigint NOT NULL DEFAULT nextval('building_id_seq'::regclass),
            "geometryType" character varying(40) COLLATE pg_catalog."default",
            type character varying(40) COLLATE pg_catalog."default",
            "PK" bigint,
            height double precision,
            geometry geometry,
            CONSTRAINT building_pkey PRIMARY KEY (id)
        );
    """)
    conn.close()


# Polygon coordinates structure in the json file is: [[[x,y], [x,y], [x,y], [x,y], [x,y]]]
# We need to convert it to POLYGON((x y, x y, x y, x y, x y))
# if coordinates array has more than one element, we need to convert it to 
# MULTIPOLYGON(((x y, x y, x y, x y, x y), (x y, x y, x y, x y, x y)))
def _convertCoordinatesToPolygon(coordinates):
    if len(coordinates) == 1:
        polygonString = 'POLYGON(('
        
        for coordinate in coordinates[0]:
            polygonString += f'{coordinate[0]} {coordinate[1]}, '
    
    else:
        polygonString = 'MULTIPOLYGON(('
        
        for polygon in coordinates:
            polygonString += '('
            
            for coordinate in polygon[0]:
                polygonString += f'{coordinate[0]} {coordinate[1]}, '
            
            polygonString = polygonString[:-2] + '), '

    # Removing the last comma and space before closing the brackets
    polygonString = polygonString[:-2] + '))'
    
    return polygonString