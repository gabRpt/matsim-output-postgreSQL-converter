# Queries

___

```python
from furbain import queries
```
___

## agentActivity()
{% method %}
_Get dataframes of the activities of agents in each zone during given timespan_

```python
agentActivity(filePath, startTime='00:00:00', endTime='32:00:00', strictTime=False)
```

**Parameters :**
* `filepath` : Path to the **geojson** file containing the different zones to consider (eg: [5zones.geojson](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/sample/5zones.geojson))
* `start_time` : start time of the timespan (string default: `'00:00:00'`)
* `end_time` : end time of the timespan (string default: `'32:00:00'`)
* `strictTime` : (boolean default: `False`)
        if true, only activities that start and end in the time interval are considered
            eg: an activity starting at 18:30:00 and ending at 19:00:00 is considered
                an activity starting at 18:30:00 and ending at 19:15:00 is NOT considered
                an activity starting at 17:00:00 and ending at 19:00:00 is NOT considered
                an activity starting starting or ending at null is NOT considered

        if false, if an activity starts before the time interval or ends after the time interval, it is considered
            eg: an activity starting at 18:00:00 and ending at xx:xx:xx is considered
                an activity starting at 18:00:00 and ending at null is considered
                an activity starting at 17:00:00 and ending at 18:00:00 or later is considered
                an activity starting at 19:00:00 and ending at xx:xx:xx is NOT considered

{% common %}
__Output :__

Returns a list of dataframes, one dataframe per zone.  
**The order of the dataframes is the order of the zones in the geojson file.**

* `id` : id of the activity
* `type` : type of the activity
* `location` : location of the activity
* `z` : z axis of the location
* `start_time` : start time of the activity
* `end_time` : end time of the activity
* `max_dur` : maximum duration of the activity
* `typeBeforeCutting` : type of the activity before cutting
* `linkId` : linkId of the activity
* `facilityId` : facilityId of the activity
* `personId` : id of the agent
* `total_time_spent` : total time spent by the person in the activity
* `time_spent_in_interval` : time spent by the person in the activity in the interval

{% common %}
![Agent activity output](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/queries/agent_activity_output.png)

{% endmethod %}

___

## odMatrix()

##### Generate the od matrix

{% method %}

_Get od matrix of trips between zones during given timespan_

```python
odMatrix(filePath, startTime='00:00:00', endTime='32:00:00', ignoreArrivalTime=True, generateArabesqueFiles=False)
```

**Parameters :**
* `filepath` : Path to the **geojson** file containing the different zones to consider (eg: [5zones.geojson](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/sample/5zones.geojson))
* `start_time` : start time of the timespan (string default: `'00:00:00'`)
* `end_time` : end time of the timespan (string default: `'32:00:00'`)
* `ignoreArrivalTime` : (boolean default: `True`)
        if true, only startTime is considered
        eg: a trip having dep_time = 18:00:00 and trav_time = 00:30:00 is considered
            a trip having dep_time = 18:00:00 and trav_time = 01:30:00 is NOT considered (arrivalTime = 19:30:00 is not in interval)
        if False:
        eg : a trip having dep_time = 18:00:00 and trav_time = 00:30:00 is considered
                a trip having dep_time = 18:00:00 and trav_time = 01:30:00 is considered
        in both cases, if a trip has a dep_time < 18:00:00 it will not be considered
* `generateArabesqueFiles` : if true, generates the files needed to create a scheme in [Arabesque](http://arabesque.ifsttar.fr/) (boolean default: `False`)

{% common %}
__Output :__

A 2D array.

![OD Matrix output](https://raw.githubusercontent.com/gabRpt/matsim-output-postgreSQL-converter/main/resources/docs/queries/OD_matrix_output.png)


{% endmethod %}

##### Use generated files in Arabesque

{% method %}

If `generateArabesqueFiles` is set to true, the files needed to create a scheme in [Arabesque](http://arabesque.ifsttar.fr/) are generated in the folder `/output`.
You will get 2 files :
* `flow.csv` : contains the od matrix of the trips between zones
* `location.csv` : contains the zones with their coordinates

_**A detailed documentation on how to create a scheme in Arabesque can be found [here](https://gflowiz.github.io/arabesque/).**_

{% endmethod %}

___

## activitySequences()
{% method %}
_Get the activity sequences of agents during given timespan and zone_

**MULTIPROCESSING IS UNSTABLE, YOU SHOULD USE THIS FUNCTION ALONE IN A SCRIPT**

```python
activitySequences(filePath, startTime='00:00:00', endTime='32:00:00', interval=15, batchSize=10, createTableInDatabase=False, nbAgentsToProcess=-1)
```

**Parameters :**
* `filepath` : Path to the **geojson** file containing **only one** zone consider (eg: [1zone.geojson](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/sample/1zone.geojson))
* `start_time` : start time of the timespan (string default: `'00:00:00'`)
* `end_time` : end time of the timespan (string default: `'32:00:00'`)
* `interval` : interval of time between each sequence (in minutes => int default: `15`)
* `batchSize` : number of agents to consider in each batch to optimize multiprocessing (has to be > 0, int default: `10`)
* `createTableInDatabase` : if true, creates a table in the database with the activity sequences, the name of the table can be defined in the config file (boolean default: `False`)
* `nbAgentsToProcess` : number of agents to process, if set at 100 it will process the first 100 agents. If set at -1 it will process all agents (int default: `-1`)

{% common %}
__Output :__

Returns a dataframe with all the activity sequences of all the agents that have **at least one** activity in the given zone during the given timespan.
The dataframe has the following columns :

* `agentId` : id of the agent
* `periodStart` : start time of the current period
* `periodEnd` : end time of the current period
* `mainActivityId` : id of the activity the agent spent the most time in during the current period
* `startActivityId` : id of the first activity of the agent during the current period
* `endActivityId` : id of the last activity of the agent during the current period
* `mainActivityStartTime` : start time of the activity the agent spent the most time in during the current period
* `mainActivityEndTime` : end time of the activity the agent spent the most time in during the current period
* `timeSpentInMainActivity` : time spent by the agent in the activity the agent spent the most time in during the current period
{% endmethod %}