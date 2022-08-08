import collections
import config
import tools
import geopandas as gpd
import pandas as pd
import json
from geoalchemy2 import Geometry

def importBuildings():
    print('')
    
    with open(config.PATH_BUILDINGS, 'r') as buildingsJson:
        buildings = json.load(buildingsJson)        
        polygonFeaturesDict = collections.defaultdict(list)
        multiPolygonFeaturesDict = collections.defaultdict(list)
        
        for feature in buildings['features']:
            # Checking if the feature has coordinates
            if len(feature['geometry']['coordinates'][0]) == 0:
                continue
            
            # Checking supported geometry type
            if feature['geometry']['type'] == 'Polygon':
                polygonString = _convertCoordinatesToPolygon(feature['geometry']['coordinates'])
                polygonFeaturesDict['geometryType'].append(feature['geometry']['type'])
                polygonFeaturesDict['type'].append(feature['type'])
                polygonFeaturesDict['PK'].append(feature['properties']['PK'])
                polygonFeaturesDict['height'].append(feature['properties']['HEIGHT'])         
                polygonFeaturesDict['geometry'].append(polygonString)
                
            elif feature['geometry']['type'] == 'MultiPolygon':
                polygonString = _convertCoordinatesToPolygon(feature['geometry']['coordinates'])
                multiPolygonFeaturesDict['geometryType'].append(feature['geometry']['type'])
                multiPolygonFeaturesDict['type'].append(feature['type'])
                multiPolygonFeaturesDict['PK'].append(feature['properties']['PK'])
                multiPolygonFeaturesDict['height'].append(feature['properties']['HEIGHT'])         
                multiPolygonFeaturesDict['geometry'].append(polygonString)
                
            else:
                print(f'WARNING: geometry type "{feature["geometry"]["type"]}" not supported. Skipping feature.')
                continue
            
               
            # Polygon coordinates structure in the json file is: [[[x,y], [x,y], [x,y], [x,y], [x,y]]]
            # We need to convert it to POLYGON((x y, x y, x y, x y, x y))
            
        
        polygonDataframe = pd.DataFrame(polygonFeaturesDict)
        print(polygonDataframe)
        
        multiPolygonDataframe = pd.DataFrame(multiPolygonFeaturesDict)
        print(multiPolygonDataframe)
        
        conn = tools.connectToDatabase()
        polygonDataframe.to_sql('building', con=conn, if_exists='append', index=False, dtype={'geom': Geometry('POLYGON', srid=config.DB_SRID)})
        multiPolygonDataframe.to_sql('building', con=conn, if_exists='append', index=False, dtype={'geom': Geometry('MULTIPOLYGON', srid=config.DB_SRID)})


def _convertCoordinatesToPolygon(coordinates):
    if len(coordinates) == 1:
        polygonString = 'POLYGON(('
        
        for coordinate in coordinates[0]:
            polygonString += f'{coordinate[0]} {coordinate[1]}, '
    
        polygonString = polygonString[:-2] + '))'

    else:
        polygonString = 'MULTIPOLYGON(('
        
        for polygon in coordinates:
            polygonString += '('
            
            for coordinate in polygon[0]:
                polygonString += f'{coordinate[0]} {coordinate[1]}, '
            
            polygonString = polygonString[:-2] + '), '
        polygonString = polygonString[:-2] + '))'
    
    return polygonString