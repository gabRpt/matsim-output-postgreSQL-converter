# Queries


___



## agent-activity
Get dataframes of the activities of agents in each zone during given timespan
In [main.py](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/src/main.py "main.py") uncomment the lines below `========= Agents activities dataframes =========`.
Edit the parameters of the function `queries.agentActivity.agentActivity` :
* `filepath` : Path to the **geojson** file containing the different zones to consider (eg: [5zones.geojson](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/5zones.geojson))
* `start_time` : start time of the timespan
* `end_time` : end time of the timespan
* `strictTime` :
        if true, only activities that start and end in the time interval are considered
            eg: an activity starting at 18:30:00 and ending at 19:00:00 is considered
                an activity starting at 18:30:00 and ending at 19:15:00 is NOT considered
                an activity starting at 17:00:00 and ending at 19:00:00 is NOT considered
        if false, if an activity starts before the time interval or ends after the time interval, it is considered
            eg: an activity starting at 18:00:00 and ending at xx:xx:xx is considered
                an activity starting at 18:00:00 and ending at null is considered
                an activity starting at 17:00:00 and ending at 18:00:00 or later is considered
                an activity starting at 19:00:00 and ending at xx:xx:xx is NOT considered

Returns a list of dataframes, one dataframe per zone.


___



## od-matrix
Get od matrix of trips between zones during given timespan
##### Generate the od matrix
In [main.py](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/src/main.py "main.py") uncomment the lines below `========= OD Matrix =========`.
Edit the parameters of the function `queries.odMatrix.odMatrix` :
* `filepath` : Path to the **geojson** file containing the different zones to consider (eg: [5zones.geojson](https://github.com/gabRpt/matsim-output-postgreSQL-converter/blob/main/resources/5zones.geojson))
* `start_time` : start time of the timespan
* `end_time` : end time of the timespan
* `ignoreArrivalTime` :
        if true, only startTime is considered
        eg: a trip having dep_time = 18:00:00 and trav_time = 00:30:00 is considered
            a trip having dep_time = 18:00:00 and trav_time = 01:30:00 is NOT considered (arrivalTime = 19:30:00 is not in interval)
        if False:
        eg : a trip having dep_time = 18:00:00 and trav_time = 00:30:00 is considered
                a trip having dep_time = 18:00:00 and trav_time = 01:30:00 is considered
        in both cases, if a trip has a dep_time < 18:00:00 it will not be considered
* `generateArabesqueFiles` : if true, generates the files needed to create a scheme in [Arabesque](http://arabesque.ifsttar.fr/)

##### Use generated files in Arabesque
If `generateArabesqueFiles` is set to true, the files needed to create a scheme in [Arabesque](http://arabesque.ifsttar.fr/) are generated in the folder `./generated`.
You will get 2 files :
* `flow.csv` : contains the od matrix of the trips between zones
* `location.csv` : contains the zones with their coordinates

_**A detailed documentation on how to create a scheme in Arabesque can be found [here](https://gflowiz.github.io/arabesque/).**_