import collections
import config
import tools
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
        
        # Importing the data to the database        
        conn = tools.connectToDatabase()
        polygonDataframe.to_sql('building', con=conn, if_exists='append', index=False, dtype={'geom': Geometry('POLYGON', srid=config.DB_SRID)})



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