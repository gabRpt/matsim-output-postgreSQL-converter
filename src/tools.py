from furbain import config
from sqlalchemy import create_engine
import subprocess

def connectToDatabase():
    engine = create_engine(f'postgresql+psycopg2://{config.getDatabaseUser()}:{config.getDatabasePassword()}@{config.getDatabaseHost()}:{config.getDatabasePort()}/{config.DB_DBNAME}')
    conn = engine.connect()
    return conn

def connectToPostgres():
    engine = create_engine(f'postgresql+psycopg2://{config.getDatabaseUser()}:{config.getDatabasePassword()}@{config.getDatabaseHost()}:{config.getDatabasePort()}')
    conn = engine.connect()
    return conn


def configureDatabase():
    conn = connectToDatabase()
    conn.execute("SET statement_timeout = 0;")
    conn.execute("SET lock_timeout = 0;")
    conn.execute("SET idle_in_transaction_session_timeout = 0;")
    conn.execute("SET client_encoding = 'UTF8';")
    conn.execute("SET standard_conforming_strings = on;")
    conn.execute("SELECT pg_catalog.set_config('search_path', '', false);")
    conn.execute("SET check_function_bodies = false;")
    conn.execute("SET xmloption = content;")
    conn.execute("SET client_min_messages = warning;")
    conn.execute("SET row_security = off;")
    conn.execute("CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;")
    conn.execute("COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';")
    conn.execute("SET default_tablespace = '';")
    conn.execute("SET default_table_access_method = heap;")
    conn.close()


# Create databse will set the database as the selected database
def createDatabase(name):
    # check if the database exists
    if name in getAllDatabasesProjects():
        raise Exception(f'The database "{name}" already exists.')
    else:
        conn = connectToPostgres()
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(f'CREATE DATABASE "{name}";')
        conn.close()
        
        selectDatabase(name, False)
        configureDatabase()
        print(f'Database "{name}" created.')


# Select database that will be used in the project
def selectDatabase(name, verbose=True):
    # check if the database exists
    if name not in getAllDatabasesProjects():
        raise Exception(f'The database "{name}" does not exist.')
    else:
        config.DB_DBNAME = name
        if verbose:
            print(f'Database "{name}" selected.')
        

def getAllDatabasesProjects():
    conn = connectToDatabase()
    result = conn.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    return [row[0] for row in result.fetchall()]


def executeSQLOnDatabase(queryString):
    conn = connectToDatabase()
    result = conn.execute(queryString)
    return result.fetchall()


def getTablesFromDatabase():
    conn = connectToDatabase()
    tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return [table[0] for table in tables.fetchall()]


def deleteTable(name):
    conn = connectToDatabase()
    # check if the table exists
    if name in getTablesFromDatabase():
        conn.execute(f'DROP TABLE "{name}";')
    else:
        raise Exception(f'The table "{name}" does not exist.')

# Converts hh:mm:ss time to x days x hours x minutes x seconds
def formatTimeToIntervalType(time):
    if time is not None and isinstance(time, str):
        time = time.split(':')
        formattedTime = ""
        if int(time[0]) > 23:
            formattedTime += str(int(time[0]) // 24) + " days "
            time[0] = int(time[0]) % 24
        
        formattedTime += f'{time[0]} hours {time[1]} minutes {time[2]} seconds'
        return formattedTime
    else:
        return None
            

# Returns the time in hh:mm:ss format
def getFormattedTime(timeInSeconds):
    if timeInSeconds is not None:
        if isinstance(timeInSeconds, float):
            timeInSeconds = int(timeInSeconds)
        m, s = divmod(timeInSeconds, 60)
        h, m = divmod(m, 60)
        if h < 10:
            h = '0' + str(h)
        else:
            h = str(h)
        return f'{h}:{m:02d}:{s:02d}'
    else:
        return None

# Receive a time in a string with 'hh:mm:ss' format and return the time in seconds (int)
def getTimeInSeconds(time):
    if time is not None and isinstance(time, str):
        time = time.split(':')
        return int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
    else:
        return None

# converts a list of x lists to a string and replace Angle bracket with parenthesis
# [[[1, 2], [3,4], [5,6]]] -> "(((1,2) (3,4) (5,6)))"
def convertListToString(listToConvert):
    if isinstance(listToConvert, list):
        return " ".join(map(convertListToString, listToConvert)) + ")"
    else:
        return str(listToConvert)


# format geojson polygon to a postgis polygon
def formatGeoJSONPolygonToPostgisPolygon(coordinates, geometryType, epsg):
    polygon = convertListToString(coordinates)
    polygon = polygon.replace(") ", ", ")
    
    # Removing 1 level of parenthesis
    # (((1,2) (3,4) (5,6))) -> ((1,2) (3,4) (5,6))
    # this caused an error while creating the geometry
    nbEndingParenthesis = polygon.count(")")
    polygon = polygon[:-1]
    nbEndingParenthesis -= 1
    
    # adding nbEndingParenthesis parenthesis at the beginning
    polygon = "(" * nbEndingParenthesis + polygon    
    polygon = geometryType + polygon

    return polygon


# Return the EPSG of the geojson
# if not found return the Arabesque default EPSG
def getEPSGFromGeoJSON(gjson):
    epsg = None

    try:
        crs = gjson['crs']['properties']['name']
        
        # get the EPSG code
        for i in crs.split(':'):
            if i.isdigit():
                epsg = int(i)
                break
        
        if epsg is None:
            raise Exception("No EPSG code found in the GeoJSON file")

    except:
        print("No EPSG code found in the GeoJSON file")
        epsg = config.ARABESQUE_DEFAULT_SRID

    return epsg


def chunker(seq, size):
    # from http://stackoverflow.com/a/434328
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))