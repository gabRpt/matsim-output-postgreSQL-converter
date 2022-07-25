import config
from sqlalchemy import create_engine

connection = None

def connectToDatabase():
    global connection
    
    engine = create_engine(config.DB_CONNECTION_STRING)
    conn = engine.connect()
    return conn