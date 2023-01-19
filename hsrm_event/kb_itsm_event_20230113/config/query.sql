select
       event_date ,
       '01042420660' telephone,
       event.device_uid_zero(serial_number) dev_serial,
       event.device_alias_zero(serial_number) dev_alias,
       device_type ,
       vendor_name ,
       event_code,
       event_level,
       q_event_level,
       desc_summary,
       seq_no
from
       (
       select
               event_date ,
               serial_number ,
               device_type ,
               vendor_name ,
               event_code,
               event_level,
               q_event_level,
               desc_summary,
               seq_no
       from
               "event".event_log el
       WHERE
               1=1
               and seq_no > '{SEQ_NO}'
               and ((q_event_level = 'Warning' and device_type = 'STG') or (q_event_level = 'Critical' and device_type = 'STG')
               or (q_event_level = 'Critical' and device_type = 'SWI')
               or (q_event_level = 'Critical' and device_type = 'NAS'))

)kk1

order by
       seq_no ASC;




