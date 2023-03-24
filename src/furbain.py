import argparse
from furbain import config

def main(args=None):
    parser = argparse.ArgumentParser(description='Command line tool for furbain')
    parser.add_argument('-u', '--user', help='The user to connect to the database')
    parser.add_argument('-p', '--password', help='The password to connect to the database')
    parser.add_argument('-H', '--host', help='The host to connect to the database')
    parser.add_argument('-P', '--port', help='The port to connect to the database')
    parser.add_argument('-s', '--srid', help='The SRID of the database')
    parser.add_argument('-o', '--output', help='The path to the output folder of the matsim simulation')
    
    args = parser.parse_args(args)
    
    for arg in vars(args):
        currentArg = getattr(args, arg)
        
        if currentArg is not None:
            if arg == 'user' and currentArg:
                config.setDatabaseUser(currentArg)
            elif arg == 'password' and currentArg:
                config.setDatabasePassword(currentArg)
            elif arg == 'host' and currentArg:
                config.setDatabaseHost(currentArg)
            elif arg == 'port' and currentArg:
                config.setDatabasePort(currentArg)
            elif arg == 'srid' and currentArg:
                config.setDatabaseSRID(currentArg)
            elif arg == 'output' and currentArg:
                config.setSimulationOutputPath(currentArg)
            
            if arg == 'password':
                currentArg = '********'
            print('The ' + arg + ' has been set to ' + currentArg)