# Database Tools

___

```python
from furbain import databaseTools
```
___

## createDatabase(databaseName)
{% method %}

Function to create a database. It will set the created database as the selected database.  
**Parameters :**
* `databaseName` : Name of the database to create

{% common %}
**Output :**
* `Database "{databaseName}" created.` if success
* `The database "{databaseName}" already exists.` an exception raised
{% endmethod %}



## selectDatabase(databaseName, verbose=True)
{% method %}

Function to select database that will be used in the project  
**Parameters :**
* `databaseName` : Name of the database to select (string)
* `verbose` : print a confirmation messahe (boolean default: `True`)

{% common %}
**Output :**
* `Database "{databaseName}" selected.` if success
* `The database "{databaseName}" does not exist.` an exception raised

{% endmethod %}



## executeSQLQueryOnDatabase(queryString)
{% method %}

Function to execute a SQL query on the selected database  
**Parameters :**
* `queryString` : SQL query to execute (string)

{% common %}
**Output :**
* The results of the query

{% endmethod %}



## getAllDatabasesProjects()
{% method %}

Function to get the name of all the databases in the project

{% common %}
**Output :**
* A list of all the databases in the project

{% endmethod %}



## getTablesFromDatabase()
{% method %}
Function to get the name of all the tables in the selected database

{% common %}
**Output :**
* A list of all the tables in the selected database

{% endmethod %}



## deleteTable(tableName)
{% method %}
Function to delete a table from the selected database  
**Parameters :**
* `tableName` : Name of the table to delete (string)

{% common %}
**Output :**
* `Table "{tableName}" deleted.` if success
* `The table "{tableName}" does not exist.` an exception raised

{% endmethod %}



# getDatabaseTableDataframe(tableName)
{% method %}
Function to get a dataframe of a table from the selected database
**Parameters :**
* `tableName` : Name of the table to get (string)

{% common %}
**Output :**
* A dataframe of the table if success
* `The table "{tableName}" does not exist.` an exception raised

{% endmethod %}