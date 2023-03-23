import pathlib
import os
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='furbain',
    version='1.0.0',

    url='https://github.com/gabRpt/matsim-output-postgreSQL-converter',
    author='Gabin RAAPOTO',
    author_email='gabin.raapoto@univ-eiffel.fr',
    description="This tool converts matsim's output to a database and also provides various queries to extract data from the database.",
    long_description=README,
    
    packages=['furbain', 'furbain.queries', 'furbain.converter'],
    package_dir={'furbain':'src'},
    install_requires=[
        "geoalchemy2 >= 0.12.2",
        "geopandas >= 0.9.0",
        "pandas >= 1.4.3",
        "sqlalchemy >= 1.4.39, <= 1.4.46", # https://stackoverflow.com/questions/75315117/attributeerror-connection-object-has-no-attribute-connect-when-use-df-to-sq
        "shapely >= 1.7.1",
        "tqdm >= 4.64.1",
        "pyproj >= 2.6.1",
        "geojson >= 2.5.0",
        "protobuf == 3.20.0",
        "psycopg2 == 2.9.3",
        f"matsim_tools @ file://localhost/{os.getcwd()}/resources/setup/matsim_tools-1.0.5-py3-none-any.whl"
    ],
    entry_points={
        'console_scripts': [
            'setDbUser=furbain.config:cmdSetDatabaseUser',
        ],
    },
)