create view count_location_chemical_weekday as
with wd_num_to_text as (
    select 0 id, 'SUN' val union
    select 1 id, 'MON' val union
    select 2 id, 'TUE' val union
    select 3 id, 'WED' val union
    select 4 id, 'THU' val union
    select 5 id, 'FRI' val union
    select 6 id, 'SAT' val
)
select a.location
     , a.chemical 
     , b.val day_of_week
     , count(a.id) total
from waterway_reading_master a
inner join wd_num_to_text b on cast(strftime('%w', a.sample_date) as integer) = b.id 
group by a.chemical
       , a.location
       , strftime('%w', a.sample_date) 
order by location asc
       , chemical asc
       , total desc
