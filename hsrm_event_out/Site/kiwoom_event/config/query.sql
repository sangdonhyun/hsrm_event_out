select
       event_date ,
       serial_number ,
       device_type ,
       view.device_alias_zero(serial_number) dev_alias,
       vendor_name ,
       desc_summary,
       event_code
from
       "event".event_log el
where
    1=1
    --and log_date >= '{YD}'::date
    --and log_date <= '{TD}'::date
    --and q_event_level = 'Critical'
    and check_date >='{CD}'
order by 1, 2
