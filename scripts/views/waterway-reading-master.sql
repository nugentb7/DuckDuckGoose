create view waterway_reading_master as 
select ww.id
        , ww.value 
        , cast(cast(um.unit_name as blob) as varchar2) unit_name
        , cm.display as chemical
        , l.display as location
        , ww.sample_date
from waterway_reading ww 
left join location l on ww.location_id = l.id
left join chemical cm on ww.chemical_id = cm.id
left join unit_of_measure um on cm.unit_of_measure_id = um.id