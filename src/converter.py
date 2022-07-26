import matsim
import config
import tools
import pandas as pd
import geopandas as gpd
import numpy as np
from geoalchemy2 import Geometry

def importVehicles():
    vehicleDataframes = matsim.Vehicle.vehicle_reader(config.PATH_ALLVEHICLE)
    vehicleTypes = vehicleDataframes.vehicle_types
    vehicles = vehicleDataframes.vehicles
    
    # Renamming the columns to match the database
    vehicleTypes.rename(columns={
        'pce':'passengerCarEquivalents',
        'factor': 'flowEfficiencyFactor'
    }, inplace = True)
    
    vehicles.rename(columns={
        'type': 'vehicleTypeId'
    }, inplace = True)
    
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    vehicleTypes.to_sql('vehicleType', con=conn, if_exists='append', index=False)
    vehicles.to_sql('vehicle', con=conn, if_exists='append', index=False)


def importHouseholds():
    householdReader = matsim.Household.houshold_reader(config.PATH_HOUSEHOLDS)
    householdDataframe = householdReader.households
    
    # Formating dataframe
    householdDataframe.drop(columns=['members'], inplace=True)
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    householdDataframe.to_sql('household', con=conn, if_exists='append', index=False)


def importPersons():
    personsDataframe = pd.read_csv(config.PATH_PERSONS, sep=';')
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
    personGeoDataframe.to_sql('person', con=conn, if_exists='append', index=False, dtype={'first_act_coord': Geometry('POINT', srid=config.DB_SRID)})


# TODO Optimize this function by modifying matsim package
# -> Modify Network.py to return add or modify network reader, to return links links with their attributes in the same dataframe
# -> LineString conversion to Geometry
def importNetworkLinks():
    network = matsim.Network.read_network(config.PATH_NETWORK)
    nodes = gpd.GeoDataFrame(network.nodes)
    links = network.links
    nodeAttributes = network.node_attrs
    linkAttributes = network.link_attrs
    
    # Renaming the attributes columns to match the database
    attributesColumnsNames = linkAttributes.name.unique()
    finalLinksAttributes = {'link_id': []}
    for column in attributesColumnsNames:
        finalLinksAttributes[column] = [] 
    
    # Creating a dataframe with the links attributes for each link
    currentLinkId = linkAttributes.iloc[0]['link_id']
    currentElementAttributes = {'link_id': currentLinkId}
    
    for index, row in linkAttributes.iterrows():
        if row['link_id'] != currentLinkId:
            for column in finalLinksAttributes:
                if column in currentElementAttributes:
                    finalLinksAttributes[column].append(currentElementAttributes[column])
                else:
                    finalLinksAttributes[column].append(None)
            currentLinkId = row['link_id']
            currentElementAttributes = {'link_id': currentLinkId}

        currentElementAttributes[row['name']] = row['value']
    
    linksAttributesDataframe = pd.DataFrame.from_dict(finalLinksAttributes)
    
    # Merging the links attributes with the links dataframe in a geodataframe
    links = gpd.GeoDataFrame(pd.merge(links, linksAttributesDataframe, on='link_id', how='left'))
    
    
    # Creating points from nodes coordinates
    nodes['point'] = nodes.apply(lambda row: 'POINT({} {})'.format(row['x'], row['y']), axis=1)
    nodes.drop(columns=['x', 'y'], inplace=True)
    
    
    # Creating geometric lines from links.from and links.to
    print('================')
    links['geom'] = links.apply(lambda row: 'LINESTRING({} {})'.format(nodes[nodes['node_id'] == row['from_node']]['point'], nodes[nodes['node_id'] == row['to_node']]['point']), axis=1)
    links.drop(columns=['from_node', 'to_node'], inplace=True)
    
    
    # Renaming the columns to match the database
    links.rename(columns={
        'link_id': 'id',
    }, inplace = True)
    
    for columnName in attributesColumnsNames:
        links.rename(columns={
            columnName: columnName.replace(':', '_')
        }, inplace = True)
    
    
    # Importing the data to the database
    conn = tools.connectToDatabase()
    links.to_sql('networkLink', con=conn, if_exists='append', index=False, dtype={'geom': Geometry('LINESTRING', srid=config.DB_SRID)})
    
    
    # print(links.dtypes)
    # print(nodes[nodes['node_id'] == links.iloc[0]['from_node']]['point'])
    # print(nodes.dtypes)
    # print(nodeAttributes.dtypes)
    # print(links.dtypes)
    # print(linkAttributes.dtypes)
    # print(finalAttributesColumnsNames)

def importFacilities():
    pass

def importTrips():
    pass

def importActivities():
    pass

def importEvents():
    pass