-- log_date >= '{YD}'::date,
-- and log_date <= '{TD}'::date,
-- and q_event_level = 'Critical'
-- and check_date >='{CD}'

SELECT
event_date,
serial_number,
event_code,
event_level,
q_event_level ,
device_type ,
al.device_alias,
desc_summary
seq_no
FROM EVENT.event_log el LEFT JOIN
 (
    SELECT stg_serial ss, stg_alias device_alias FROM master.master_stg_info msi
    UNION ALL
    SELECT nas_name ss,nas_alias device_alias FROM master.master_nas_info mni
    UNION ALL
    SELECT swi_serial ss,swi_serial device_alias FROM master.master_swi_info
) al
ON el.serial_number = al.ss
WHERE
    1 = 1
    and (((q_event_level = 'Warning' and device_type = 'STG') or (q_event_level = 'Critical'  and device_type = 'STG'))
    or (q_event_level = 'Critical'  and device_type = 'SWI')
    --or (q_event_level = 'Critical' and device_type = 'NAS')
   )
    and seq_no > '{LAST_SEQ_NO}'

order BY seq_no ASC limit 30

