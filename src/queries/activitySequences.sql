SELECT *, 
    CASE
        WHEN '00:00:00' <= start_time and '10:00:00' >= end_time then end_time - start_time
        WHEN '00:00:00' >= start_time and '10:00:00' >= end_time then end_time - '00:00:00'
        WHEN '00:00:00' > start_time and '10:00:00' < end_time then TIME '10:00:00' - TIME '00:00:00'
        WHEN '00:00:00' <= start_time and '10:00:00' <= end_time then '10:00:00' - start_time
        ELSE '10:00:00' - start_time
    END as activity_time_spent_in_interval
from activity 
where ST_Contains(ST_GeomFromText('MultiPolygon(((351418.223748 6692427.176065, 349328.175931 6689017.785563, 352097.489288 6688377.708419, 353651.962352 6691120.896179, 351418.223748 6692427.176065)))'), "location")
and (start_time between '00:00:00' and '10:00:00' or start_time is null)
and (end_time between '00:00:00' and '10:00:00' or end_time is null)
and "personId" = 95254
order by start_time asc