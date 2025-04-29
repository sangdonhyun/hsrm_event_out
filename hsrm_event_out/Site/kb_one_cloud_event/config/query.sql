select
    event_date,
    serial_number,
    event_code,
    event_level,
    q_event_level ,
    device_type ,
    al.device_alias,
    desc_summary,
    seq_no
from
    EVENT.event_log el
left join
 (
    select
        stg_serial ss,
        stg_alias device_alias
    from
        master.master_stg_info msi
union all
    select
        nas_name ss,
        nas_alias device_alias
    from
        master.master_nas_info mni
union all
    select
        swi_serial ss,
        swi_serial device_alias
    from
        master.master_swi_info
) al
on
    el.serial_number = al.ss
where
    1 = 1
    and ((q_event_level = 'Warning'
        and device_type = 'STG')
    or (q_event_level = 'Critical'
        and device_type = 'STG')
    or (q_event_level = 'Critical'
        and device_type = 'SWI')
    --or (q_event_level = 'Critical' and device_type = 'NAS')
   )
    and seq_no > '{LAST_SEQ_NO}'
    and serial_number in (
        select
            stg_serial ss
        from
            master.master_stg_info msi
        where
            stg_biz_name::text like '%ONE_CLOUD%'
        union all
            select
                lsspi.swi_serial
            from
                live.live_swi_std_port_info lsspi
            where
                lsspi.dev_type::text = 'STG'::text
            and (lsspi.dev_name::bpchar in (
            select
                stg_serial ss
            from
                master.master_stg_info msi
            where
                stg_biz_name::text like '%ONE_CLOUD%'
                )
                        )
        group by
            lsspi.swi_serial
   )
order BY seq_no asc limit 30
