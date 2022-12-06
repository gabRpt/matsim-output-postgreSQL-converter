SELECT *,
    CASE
        WHEN '00:00:00' <= start_time and '32:00:00' >= end_time then end_time - start_time
        WHEN '00:00:00' >= start_time and '32:00:00' >= end_time then end_time - '00:00:00'
        WHEN '00:00:00' > start_time and '32:00:00' < end_time then interval '32:00:00' - interval '00:00:00'
        WHEN '00:00:00' <= start_time and '32:00:00' <= end_time then '32:00:00' - start_time
        WHEN start_time is null and '32:00:00' >= end_time then end_time - '00:00:00'
        WHEN start_time is null and '32:00:00' < end_time then interval '32:00:00' - interval '00:00:00'
        WHEN '00:00:00' > start_time and end_time is null then interval '32:00:00' - interval '00:00:00'
        WHEN '00:00:00' <= start_time and end_time is null then '32:00:00' - start_time
        WHEN start_time is null and end_time is null then interval '32:00:00' - interval '00:00:00'
    END as activity_time_spent_in_interval
from activity
where ST_Contains(ST_GeomFromText('Polygon((368105.949286 6703635.057483, 340621.820494 6703661.183081, 340909.202068 6680566.154704, 368680.712436 6680801.285083, 368105.949286 6703635.057483))'), "location")
and (start_time between '00:00:00' and '32:00:00' or start_time is null)
and (end_time between '00:00:00' and '32:00:00' or end_time is null)
order by start_time asc