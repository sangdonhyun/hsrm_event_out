import cx_Oracle
from datetime import datetime
import os

oracle_path = 'E:\\instantclient_21_6'
os.environ['PATH'] = '{};{}'.format(oracle_path,os.environ['PATH'])

# 오라클 DB 연결
#-------------------------------
connStr = 'fleta/fleta123@121.170.193.203:1522/ORCL'
conn = cx_Oracle.connect(connStr)
cur = conn.cursor()
#--------------------------------



# Insert 예 1
#
#INSERT INTO em_mmt_tran(mt_pr,subject,content,attach_file_group_key,callback,service_type,broadcast_yn,msg_status,recipient_num) values
#(sq_em_mmt_tran_01.nextval,'title test','본문테스트','0','02-2644-2241','3','N','1','01042420660');

sql = "insert into em_mmt_tran (mt_pr, date_client_req,subject,content,attach_file_group_key,callback,service_type,broadcast_yn,msg_status,recipient_num) values (sq_em_mmt_tran_01.nextval, sysdate,'subject test','본문테스트','0','02-2644-2241','3','N','1','01042420660')"

sql = """
insert into em_mmt_tran (
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
    ) values (
      sq_em_mmt_tran_01.nextval, 
      sysdate,
      'subject test',
      '본문테스트',
      '0',
      '02-2644-2241',
      '3',
      'N',
      '1',
      '01042420660'
    )
      """

cur.execute(sql)
# sql = """INSERT INTO em_mmt_tran(
#     mt_pr,
#     date_client_req,
#     subject
#
# ) values (
#     sq_em_mmt_tran_01.nextval,
#     sysdate,
#     :subject
#
#     )
# """
# #(sq_em_mmt_tran_01.nextval,'title test','본문테스트','0','02-2644-2241','3','N','1','01042420660');


# cur.execute(sql,('title test'))
conn.commit()
#
# # Insert 예 2
# sql = 'insert into logtable (name, log_date) values (:1, :2, :3)'
# cur.execute(sql, '홍길순', datetime(2021, 1, 1))
# conn.commit()
#
# # Insert 예 3 (여러 줄을 한번에 삽입)
# data_list = [( '홍길동', datetime(2021, 1, 1) ),( '김철수', datetime(2021, 1, 1) )]
# sql =  'insert into "test".logtable (name, date) values (:1, :2, :3)'
# cur.executemany(sql, data_list)
# conn.commit()
#
# # Update 예
# sql = 'update "test".logtable set name=:1 where name=:2'
# cur.execute(sql, ('수알치', '수리부엉이'))
# conn.commit()
#
# # Select 예
# sql = 'select * from "test".logtable order by name'
# cur.execute(sql)
# records = cur.feachall()
# print(records)
#
# # Delete 예
# sql = 'delete from "test".logtable where name=:1'
# cur.execute(sql, ('수리부엉이'))
# conn.commit()

#-------------------------------
# 오라클 DB 연결 해제
cur.close()    # 커서 객체 닫음 (메모리 누수 방지)
conn.close()  # 디비 연결 해제
#--------------------------------