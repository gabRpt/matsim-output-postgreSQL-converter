from furbain import config
from sqlalchemy import create_engine

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
        print(f'Table "{name}" deleted.')
    else:
        raise Exception(f'The table "{name}" does not exist.')