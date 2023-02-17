# Database
## Database structure
You can see the following diagram more in details at https://dbdiagram.io/d/62bc660c69be0b672c6841b3

Or you can check the database documentation here : https://dbdocs.io/gabRpt/matsim_output_postgreSQL_converter

![Diagram available at https://dbdiagram.io/d/62bc660c69be0b672c6841b3](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/database/database_diagram.png)

## Matsim files and tables

Here are the files used to generate each table :

| Table name  | Files used |
| ------------- | ------------- |
| activity  | output_plans.xml.gz / output_experienced_plans.xml.gz / output_facilities.xml.gz |
| building | BUILDINGS.geojson |
| facility | output_facilities.xml.gz |
| household | output_households.xml.gz |
| networdlink | output_network.xml.gz |
| networdlinkTraffic | output_events.xml.gz |
| person  | output_persons.csv.gz |
| trip | output_trips.csv.gz |
| vehicle | output_allvehicles.xml.gz |
| vehicleType | output_allvehicles.xml.gz |