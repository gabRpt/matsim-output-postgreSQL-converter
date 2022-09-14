SELECT *
from trip
where trip.id IN (SELECT t.id
        from facility f
        join trip t ON t.start_facility_id = f.id
        where ST_Contains(ST_GeomFromText('MULTIPOLYGON (((357709.594247 6694164.528312, 357977.381623 6694151.465514, 357987.178722 6694463.339836, 357717.758496 6694499.262533, 357709.594247 6694164.528312)))'), "location"))
AND trip.id IN  (SELECT t.id
        from facility f
        join trip t ON t.end_facility_id = f.id
        where ST_Contains(ST_GeomFromText('MULTIPOLYGON (((357709.594247 6694164.528312, 357977.381623 6694151.465514, 357987.178722 6694463.339836, 357717.758496 6694499.262533, 357709.594247 6694164.528312)))'), "location"))


SELECT *
from trip
where trip.id IN (SELECT t.id
        from facility f
        join trip t ON t.start_facility_id = f.id
        where ST_Contains(ST_GeomFromText('MULTIPOLYGON (((357709.594247 6694164.528312, 357977.381623 6694151.465514, 357987.178722 6694463.339836, 357717.758496 6694499.262533, 357709.594247 6694164.528312)))'), "location"))
AND trip.id IN  (SELECT t.id
        from facility f
        join trip t ON t.end_facility_id = f.id
        where ST_Contains(ST_GeomFromText('MULTIPOLYGON (((357709.594247 6694164.528312, 357977.381623 6694151.465514, 357987.178722 6694463.339836, 357717.758496 6694499.262533, 357709.594247 6694164.528312)))'), "location"))
and dep_time < '15:00:00'
and (dep_time + trav_time) > '14:30:00'
and (dep_time + trav_time) < '15:00:00'