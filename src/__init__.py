import pathlib

# TODO Maybe remove this 

# Create the config file if it doesn't exist
fileToCreate = pathlib.Path.home() / '.furbain' / 'config.json'
if not fileToCreate.exists():
    fileToCreate.parent.mkdir(parents=True, exist_ok=True)
    fileToCreate.touch()
    fileToCreate.write_text(
        """{
            "db_host": "localhost",
            "db_port": "5432",
            "db_user": "postgres",
            "db_password": "postgres",
        }""")