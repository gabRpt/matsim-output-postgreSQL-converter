import pathlib
import os
from setuptools import setup, find_packages

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
    
    packages=['src', 'src.queries', 'src.converter'],
    install_requires=[
        "geoalchemy2 >= 0.12.2",
        "geopandas >= 0.9.0",
        "pandas >= 1.4.3",
        "sqlalchemy >= 1.4.39",
        "shapely >= 1.7.1",
        "tqdm >= 4.64.1",
        "pyproj >= 2.6.1",
        f"matsim_tools @ file://localhost/{os.getcwd()}/resources/setup/matsim_tools-1.0.5-py3-none-any.whl"
    ],
)