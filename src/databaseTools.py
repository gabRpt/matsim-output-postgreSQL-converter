from furbain import config
from sqlalchemy import create_engine
import pandas as pd


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
def createDatabase(databaseName):
    # check if the database exists
    if databaseName in getAllDatabasesProjects():
        raise Exception(f'The database "{databaseName}" already exists.')
    else:
        conn = connectToPostgres()
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(f'CREATE DATABASE "{databaseName}";')
        conn.close()
        
        selectDatabase(databaseName, False)
        configureDatabase()
        print(f'Database "{databaseName}" created.')


# Select database that will be used in the project
def selectDatabase(databaseName, verbose=True):
    # check if the database exists
    if databaseName not in getAllDatabasesProjects():
        raise Exception(f'The database "{databaseName}" does not exist.')
    else:
        config.DB_DBNAME = databaseName
        if verbose:
            print(f'Database "{databaseName}" selected.')
        

def getAllDatabasesProjects():
    conn = connectToDatabase()
    result = conn.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    return [row[0] for row in result.fetchall()]


def executeSQLQueryOnDatabase(queryString):
    conn = connectToDatabase()
    result = conn.execute(queryString)
    return result.fetchall()


def getTablesFromDatabase():
    conn = connectToDatabase()
    tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    return [table[0] for table in tables.fetchall()]


def deleteTable(tableName):
    conn = connectToDatabase()
    # check if the table exists
    if tableName in getTablesFromDatabase():
        conn.execute(f'DROP TABLE "{tableName}";')
        print(f'Table "{tableName}" deleted.')
    else:
        raise Exception(f'The table "{tableName}" does not exist.')


# Returns a dataframe with the data from the table
def getDatabaseTableDataframe(tableName):
    conn = connectToDatabase()
    if tableName in getTablesFromDatabase():
        return pd.read_sql(f'SELECT * FROM "{tableName}";', conn)
    else:
        raise Exception(f'The table "{tableName}" does not exist.')