import mariadb
import sys
import datetime

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="event_user",
        password="fleta0901!",
        host="localhost",
        port=3306,
        database="event"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
#
# # Get Cursor
cur = conn.cursor()

evt_info = dict()
evt_info['evt_name'] = '0001'
evt_info['evt_info'] = 'info'
evt_info['evt_msg'] = 'this is test msg'
evt_info['evt_method'] = 'stg'
evt_info['evt_level'] = '0001'
evt_info['ins_datetime'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M%S')

sql = """INSERT INTO event.evt_tb
(evt_name, evt_info, evt_msg, evt_method, evt_level, evt_datetime, ins_datetime)
VALUES(%s, %s, %s, %s, %s, now(), %s);
"""
"""
INSERT INTO BIZ_MSG ( 
MSG_TYPE, CMID, REQUEST_TIME, SEND_TIME, DEST_PHONE, SEND_PHONE, MSG_BODY)

VALUES (
0, NOW(6), NOW(), NOW(), 
'01012341234', '0212341234', '본 메시지는 SMS 테스트 메시지 입니다.')
"""
print(sql)
cur.execute(sql, (evt_info['evt_name'],evt_info['evt_name'],
                     evt_info['evt_msg'],evt_info['evt_method'],
                     evt_info['evt_level'], evt_info['ins_datetime']))
# cur.execute(query_str)
conn.commit()

sql = "SELECT * FROM event.evt_tb order by seq_no desc limit 1"

cur.execute(sql)
results = cur.fetchall()
print(results)

cur.close()
conn.close()

