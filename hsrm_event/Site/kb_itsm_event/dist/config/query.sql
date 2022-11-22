-- log_date >= '{YD}'::date,
-- and log_date <= '{TD}'::date,
-- and q_event_level = 'Critical'
-- and check_date >='{CD}'

select
    event_date,
    serial_number,
    event_code,
    event_level,
    q_event_level ,
    desc_summary
from eventsan.eventsan_log el 
where
    1=1
    --and log_date >= '{YD}'::date,
    --and log_date <= '{TD}'::date,
    --and check_date >='{CD}'
    AND log_date >= '2022-03-01'::date
    --and log_date <= '2022-03-31'::date
    and check_date >='2022-03-16 08:36:32'
union all
select
   event_date,
    serial_number,
    event_code,
    event_level,
    q_event_level ,
    desc_summary
from EVENT.event_log sl
where
    1=1
    --and log_date >= '{YD}'::date,
    --and log_date <= '{TD}'::date,
    --and check_date >='{CD}'
    AND log_date >= '2022-03-01'::date
    --and log_date <= '2022-03-31'::date
    and check_date >='2022-03-16 08:36:32'