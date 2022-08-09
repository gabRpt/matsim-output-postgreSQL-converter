import matsim.Network as Network
import config
import tools
import pandas as pd
import geopandas as gpd
from geoalchemy2 import Geometry
from shapely.geometry import LineString



# if useDetailedNetworkFile is True, the geometry of the links found in the detailed network file will replace the geometry of the links found in the network file
def importNetworkLinks(useDetailedNetworkFile=True):
    network = Network.read_network(config.PATH_NETWORK)
    nodes = gpd.GeoDataFrame(network.nodes)
    links = network.links
    linkAttributes = network.link_attrs
    
    
    # Creating lines in links from "from_node" and "to_node" coordinates
    # attach xy to links
    full_net = (links
    .merge(nodes,
            left_on='from_node',
            right_on='node_id')
    .merge(nodes,
            left_on='to_node',
            right_on='node_id',
            suffixes=('_from_node', '_to_node'))
    )

    # create the geometry column from coordinates
    geometry = [LineString([(ox,oy), (dx,dy)]) for ox, oy, dx, dy in zip(full_net.x_from_node, full_net.y_from_node, full_net.x_to_node, full_net.y_to_node)]

    # build the geopandas geodataframe
    links = (gpd.GeoDataFrame(full_net,
        geometry=geometry)
        .drop(columns=['x_from_node','y_from_node','node_id_from_node','node_id_to_node','x_to_node','y_to_node'])
    )
    
    # Conversion of the geometry column to object
    links['geom'] = links['geometry'].apply(lambda x: x.wkt) # creating a new geom column to avoid the error "Geometry column does not contain geometry."
    links.drop(columns=['geometry'], inplace=True)
    
    if useDetailedNetworkFile:
        detailedNetworkDataframe = pd.read_csv(config.PATH_DETAILED_NETWORK, sep=',')
        
        # Removing rows where the linestring has less than 2 coordinates
        detailedNetworkDataframe = detailedNetworkDataframe[detailedNetworkDataframe['Geometry'].apply(lambda x: len(x.split(',')) > 1)]
        detailedNetworkDict = dict(zip(detailedNetworkDataframe['LinkId'], detailedNetworkDataframe['Geometry']))
        
        # adding the geometry of the links found in the detailed network file to the links found in the network file
        for link in links.itertuples():
            if link.link_id.isdigit() and int(link.link_id) in detailedNetworkDict:
                links.loc[link.Index, 'geom'] = detailedNetworkDict[int(link.link_id)]
    
    
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
    links.to_sql(config.DB_NETWORK_TABLE, con=conn, if_exists='append', index=False, dtype={'geom': Geometry('LINESTRING', srid=config.DB_SRID)})