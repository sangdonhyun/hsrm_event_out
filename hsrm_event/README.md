# hsrm_event
event 통합 공통 모듈


hsrm_event_out.py or hsrm_event_out.exe

event_log 에서 읽어와 target 파일에 add


config/config.cfg

[common]
event_file = E:\Fleta\eventout.txt
#1: event_date yyyymmddss
#2: serial_number
#3: event_code
#4: event_level , vender event level
#5: q_event_level , hsrm event level
#6: device_type
#7: device_alias
#8: desc_summary
#[2022-09-26 00:00:53][Critical][SFP RX][N/A (JAF1542CERT)][Index:fc1/2,Slot:1,Port:2] SFP Rx Power 493.17uW [Port Speed:8, Threshold:500uW]
#[2022-09-30 00:02:25][Warning][SFP RX][N/A (1002ALJ5EM)][Index:4,Slot:N/A,Port:4] SFP Rx Power 461.2uW [Port Speed:8, Threshold:500uW], Linked Devices : [SVR] FLETA-ESXI1,FLETA-ESXI2  [STG] 200A0828B1A(N/A)

msg_format = [{1}][{5}][{6}][{7}({2})][{8}]

msg_format 의 number 는 ./config/query.sql 에서 걸러지는 쿼리의 순서

1 = event_date ,2=serial_number 의 col 로 치환 되어 event_file 엣 적재됨.

20221007 수정.

SELECT
event_date,
serial_number,
event_code,
event_level,
q_event_level ,
device_type ,
al.device_alias,
desc_summary
FROM EVENT.event_log el LEFT JOIN
 (
    SELECT stg_serial ss, stg_alias device_alias FROM master.master_stg_info msi
    UNION ALL
    SELECT nas_name ss,nas_alias device_alias FROM master.master_nas_info mni
    UNION ALL
    SELECT swi_serial ss,swi_serial device_alias FROM master.master_swi_info
) al
ON el.serial_number = al.ss


nas,storage,switch 의 alias 컬럼 추가.


20231010

이벤트 연동 방식 추가.
snmp 전송
./config.cfg
[common]
send_method = file/snmp/syslog

./config/snmp.cfg 

[snmp]
d =  218.145.246.35
c = public
o = 1.3.6.1.4.1.116
i = 218.145.246.35
g = 5
s = 23
t = 12445
v1 = 1.3.6.1.4.1.116.5.11.4.2.1 STRING {SERIAL}
v4 = 1.3.6.1.4.1.116.5.11.4.2.5 STRING {DATE}
v5 = 1.3.6.1.4.1.116.5.11.4.2.6 STRING {TIME}
v6=  1.3.6.1.4.1.116.5.11.4.2.7 STRING {MSG}

해당 site 에 맞게 수정.

syslog 전송.
q_event_level = 'Critical'
   ==> rsyslog error 로 전송

q_event_level = 'Warning'
   ==> rsyslog warning 으로로 전송
이 외에는 모두 info 전송



