select distinct "personId"
from activity
where ST_Contains(ST_GeomFromText('MultiPolygon(((351418.223748 6692427.176065, 349328.175931 6689017.785563, 352097.489288 6688377.708419, 353651.962352 6691120.896179, 351418.223748 6692427.176065)))'), "location")


SELECT *
from activity 
where ST_Contains(ST_GeomFromText('MultiPolygon(((351418.223748 6692427.176065, 349328.175931 6689017.785563, 352097.489288 6688377.708419, 353651.962352 6691120.896179, 351418.223748 6692427.176065)))'), "location")
and (start_time between '00:00:00' and '09:00:00' or start_time is null)
and (end_time between '00:00:00' and '09:00:00' or end_time is null)
and "personId" = 1000559
