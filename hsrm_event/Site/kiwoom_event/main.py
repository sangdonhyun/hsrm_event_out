import cx_Oracle
from datetime import datetime
import os

oracle_path = 'E:\instantclient_21_6'
os.environ['PATH'] = '{};{}'.format(oracle_path,os.environ['PATH'])
print(os.environ['PATH'])
# 오라클 DB 연결
#-------------------------------
connStr = 'fleta/fleta123@121.170.193.203:1522/ORCL'
print(connStr)
conn = cx_Oracle.connect(connStr)
cur = conn.cursor()
#--------------------------------
# os.environ['PATH'] = ''

# Select 예
sql="""
INSERT INTO em_mmt_tran(
            mt_pr,
            date_client_req,
            subject,
            content,
            attach_file_group_key,
            callback,
            service_type,
            broadcast_yn,
            msg_status,
            recipient_num
        ) 
        values 
        (
            sq_em_mmt_tran_01.nextval,
            sysdate,
            'HSRM Event Massage',
            '[SAN스위치 #43L10M][SWI][2022-06-13 14:25:21][Critical][SFP RX][SAN 스위치 #43L10M (BRCALJ1943L10M)][Index:1,Slot:0,Port:1] SFP Rx Power 334.2uW [Port Speed:N16, Threshold:400uW], Linked Devices : [SVR] nfddbo02  [STG] CKM00155102948(스토리지 #102948)',
            '0',
            '02-2644-2241',
            '3',
            'N',
            '1',
            '01073708147')
"""


sql="""
INSERT INTO em_mmt_tran(mt_pr,date_client_req,subject,content,attach_file_group_key,callback,service_type,broadcast_yn,msg_status,recipient_num) values 
(sq_em_mmt_tran_01.nextval,sysdate,'title test','본문테스트','0','02-2644-2241','3','N','1','01042420660');
"""
sql="""
INSERT INTO em_mmt_tran(mt_pr,date_client_req,subject,content,attach_file_group_key,callback,service_type,broadcast_yn,msg_status,recipient_num) values 
(sq_em_mmt_tran_01.nextval,sysdate,:subject,:content,:attach_file_group_key,:callback,:service_type,:broadcast_yn,:msg_status,:recipient_num);
"""

ins_col = ('title test','본문테스트','0','02-2644-2241','3','N','1','01042420660')


print(sql)
cur.execute(sql,ins_col)
conn.commit()
# records = cur.fetchall()
# print(records)

#-------------------------------
# 오라클 DB 연결 해제
cur.close()    # 커서 객체 닫음 (메모리 누수 방지)
conn.close()  # 디비 연결 해제
#--------------------------------