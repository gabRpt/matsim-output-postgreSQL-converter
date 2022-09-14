SELECT *, end_time - start_time as total_time_spent, 
    CASE
        WHEN '18:00:00' <= start_time and '18:30:00' >= end_time then end_time - start_time
        WHEN '18:00:00' >= start_time and '18:30:00' >= end_time then end_time - '18:00:00'
        WHEN '18:00:00' > start_time and '18:30:00' < end_time then TIME'18:30:00' - TIME'18:00:00'
        WHEN '18:00:00' <= start_time and '18:30:00' <= end_time then '18:30:00' - start_time
    END as time_spent_in_interval
from activity 
where ST_Contains(ST_GeomFromText('MultiPolygon(((357709.594247 6694164.528312, 357977.381623 6694151.465514, 357987.178722 6694463.339836, 357717.758496 6694499.262533, 357709.594247 6694164.528312)))'), "location")
and start_time < '18:30:00'
and (end_time > '18:00:00' or end_time is null)


SELECT *, end_time - start_time as total_time_spent, 
    CASE
        WHEN '18:00:00' <= start_time and '18:30:00' >= end_time then end_time - start_time
        WHEN '18:00:00' >= start_time and '18:30:00' >= end_time then end_time - '18:00:00'
        WHEN '18:00:00' > start_time and '18:30:00' < end_time then TIME'18:30:00' - TIME'18:00:00'
        WHEN '18:00:00' <= start_time and '18:30:00' <= end_time then '18:30:00' - start_time
    END as time_spent_in_interval
from activity 
where ST_Contains(ST_GeomFromText('MultiPolygon(((357709.594247 6694164.528312, 357977.381623 6694151.465514, 357987.178722 6694463.339836, 357717.758496 6694499.262533, 357709.594247 6694164.528312)))'), "location")
and start_time between '18:00:00' and '18:30:00'
and end_time between '18:00:00' and '18:30:00'