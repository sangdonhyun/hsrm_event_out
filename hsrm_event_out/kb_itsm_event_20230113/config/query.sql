select
       event_date ,
       telephone,
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
       where
               1=1
               and seq_no > '{SEQ_NO}'
               and ((q_event_level = 'Warning' and device_type = 'STG') or (q_event_level = 'Critical' and device_type = 'STG')
               or (q_event_level = 'Critical' and device_type = 'SWI')
               or (q_event_level = 'Critical' and device_type = 'NAS'))
)kk1
left join (
       select
               kk1.*,
                      replace(cellphone, '-', '') telephone
       from
               (
               select
                      stg_serial dev_serial,
                             trim(unnest(string_to_array(temp_2, '/'))) user_name
               from
                      master.master_stg_add_info msai
       union all
               select
                      swi_serial,
                             trim(unnest(string_to_array(temp_2, '/'))) user_name
               from
                      master.master_swi_add_info msai
       )kk1
       left join "member".member_info kk2
       on
               kk1.user_name = kk2.user_name
               or kk1.user_name = kk2.user_id
       where
               kk2.cellphone is not null
)kk2 on
       kk1.serial_number = kk2.dev_serial
where
       kk2.dev_serial is not null
order by
       seq_no asc





