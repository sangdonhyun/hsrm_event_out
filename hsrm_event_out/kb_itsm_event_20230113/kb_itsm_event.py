import psycopg2
import datetime
import socket
import json
import sys
import configparser
import os
import logging
from logging.handlers import TimedRotatingFileHandler
"""

"""

class itsm_event():
    def __init__(self):
        self.now = datetime.datetime.now()
        self.flogger = self.get_logger
        self.cfg = self.get_cfg()
        self.conn_string = self.get_conn_str()
        print(self.conn_string)
        self.c_file = os.path.join('config','c_date.txt')
        self.seq_file = os.path.join('config','seq_no.txt')
        self.last_seq_no = self.get_last_seq_no()

    def get_last_seq_no(self):
        try:
            with open(os.path.join('config', 'seq_no.txt')) as f:
                last_seq_no = f.read().strip()
        except Exception as e:
            print(str(e))
            last_seq_no = self.get_last_seq_no_in_db()
        return last_seq_no

    def get_last_seq_no_in_db(self):
        query = """SELECT max(seq_no) FROM EVENT.event_log WHERE
    1=1
        AND  ((q_event_level = 'Warning' and device_type = 'STG') or (q_event_level = 'Critical' and device_type = 'STG')
        or (q_event_level = 'Critical' and device_type = 'SWI') 
    )
        """
        try:
            seq_no = self.getRaw(query)[0][0]
        except Exception as e:
            print(str(e))
            seq_no = "1"
        with open(self.seq_file) as fw:
            fw.write(seq_no)
        return seq_no

    def set_last_seq_no(self):
        with open(self.seq_file) as f:
            last_seq_no = f.read()
        if not self.last_seq_no == last_seq_no:
            with open(self.seq_file,'w') as fw:
                fw.write(str(self.last_seq_no))

    @property
    def get_logger(self):
        if not os.path.isdir('logs'):
            os.makedirs('logs')
        formatter = logging.Formatter(u'%(asctime)s %(levelname)s ==> %(message)s')
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        stream_hander = logging.StreamHandler()
        stream_hander.setFormatter(formatter)
        logger.addHandler(stream_hander)
        log_file = os.path.join('logs',self.now.strftime('%Y%m%d.log'))
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(u'%(asctime)s %(levelname)s ==> %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger




    def get_conn_str(self):
        ip = self.cfg.get('database','ip')
        user = self.cfg.get('database','user')
        dbname = self.cfg.get('database','dbname')
        password = self.cfg.get('database','password')
        port = self.cfg.get('database','port',fallback=5432)
        return "host='{}' dbname='{}' user='{}' password='{}' port ='{}'".format(ip,dbname,user,password,port)

    def get_cfg(self):
        cfg = configparser.RawConfigParser()
        cfg_file = os.path.join('config','config.cfg')
        cfg.read(cfg_file)
        return cfg

    def getRaw(self, query_string):
        # print(query_string)
        db = psycopg2.connect(self.conn_string)

        try:
            cursor = db.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()

            cursor.close()
            db.close()

            return rows
        except Exception as e:
            self.flogger.error(str(e))
            return []


    def send(self,msg):
        """
        [itsm]
        itsm_ip = 121.170.193.222
        itsm_port = 3264
        :return:
        """
        host = self.cfg.get('itsm', 'itsm_ip', fallback='127.0.0.1')
        port = self.cfg.get('itsm', 'itsm_port', fallback=3264)
        port = int(port)
        print(host,port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            sock.connect((host, port))
            if isinstance(msg,str):
                msg=msg.encode()
            sock.sendall(msg)
        except socket.error as e:
            self.flogger.error(str(e))
        finally:
            sock.close()

    def get_evt_list(self,yd,td,cd):
        """
        evt = {'datetime':'20220399120000', 'dev': 'STG', 'serial': '20924', 'message': 'Test event from HSRM', "tel_num": '01042420660'}
        evt_list.append(evt)
        :param yd:
        :param td:
        :param cd:
        :return:
        """
        evt_list = list()
        q_file = os.path.join('config','query.sql')
        with open(q_file) as f:
            q=f.read()
        q = q.replace('{YD}',yd)
        q = q.replace('{TD}',td)
        q = q.replace('{CD}',cd)
        if '{SEQ_NO}' in q:
            q = q.replace('{SEQ_NO}', self.last_seq_no)

        print(q)
        q_list = self.getRaw(q)
        """
        2022-03-04 09:20:55	01077778888	00000000000000011015	411015	STG	HITACHI	is a Error test code.[PORT:5E]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        2022-03-15 10:35:55	01077778888	00000000000000011536	11536	STG	HITACHI	is a Error test code.[PORT:5E]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        2022-03-15 10:35:55	01077778888	00000000000000011537	11537	STG	HITACHI	is a Error test code.[PORT:5E]
        """
        if len(q_list) > 0:
            self.flogger.info(q)
        for evt in q_list:
            evt_info = dict()
            date_str = datetime.datetime.strftime(datetime.datetime.strptime(evt[0],'%Y-%m-%d %H:%M:%S'),'%Y%m%d%H%M%S')
            evt_info['event_date'] = date_str
            evt_info['tel_num'] = evt[1]
            evt_info['dev_serail'] = evt[2]
            evt_info['dev_alias'] = evt[3]
            try:
                evt_info['dev_type'] = evt[4].strip()
            except Exception as e:
                evt_info['dev_type'] = ''
            try:
                evt_info['dev_vedor'] = evt[5].strip()
            except Exception as e:
                evt_info['dev_vedor'] = ''
            try:
                evt_info['evt_desc'] = evt[9].strip()
            except Exception as e:
                evt_info['evt_desc'] = ''
            evt_list.append(evt_info)
            self.last_seq_no = evt[-1]
            print(evt)
            print(evt_info)
        return evt_list

    def get_req(self):
        req_info = dict()
        for opt in self.cfg.options('message'):
            req_info[opt] = self.cfg.get('message',opt)
        return req_info

    def get_1min_date(self,cdate):
        cd_t=datetime.datetime.strptime(cdate,'%Y-%m-%d %H:%M:%S')
        qcd = cd_t - datetime.timedelta(minutes=1)
        return qcd.strftime('%Y-%m-%d %H:%M:%S')

    def get_cdate(self):
        cd = self.now - datetime.timedelta(days=1)
        cdate = cd.strftime('%Y-%m-%d %H:%M:%S')
        if os.path.isfile(self.c_file):
            with open(self.c_file) as f:
                cdate = f.read()
        qcdate = self.get_1min_date(cdate)
        #date 변수 셋팅
        self.set_cdate()
        return qcdate,cdate

    def set_cdate(self):
        with open(self.c_file,'w') as fw:
            fw.write(self.now.strftime('%Y-%m-%d %H:%M:%S'))
        print('check date  : ',self.now.strftime('%Y-%m-%d %H:%M:%S'))

    def get_log_str(self):
        log_file = os.path.join('logs',self.now.strftime('%Y%m%d.log'))
        with open(log_file) as f:
            log_str = f.read()
        return log_str

    def main(self):
        yd_date = self.now - datetime.timedelta(days=1)
        yd = yd_date.strftime('%Y-%m-%d')
        td = self.now.strftime('%Y-%m-%d')
        qcd,cd = self.get_cdate()
        evt_list = self.get_evt_list(yd, td, qcd)

        print('event count :',len(evt_list))
        """
        KB ITSM
        INFO  : 구분자
        2  : {1 :수신직원번소 , 2:수신전화번호, 3:수신App코드그룹, 6:ITSM정의수신코드} => 2번고정
        01012341234  : 수신대상자 (전화번호) event message 대상자.
        20220329120000 : 이벤트 발생시간.
        5011815 : 요청자 (KB 담당 직원번호)
        P : 발송타입 , 고정값
        HSRM : app code 값
        HSRM : 프로그램명
        NA : 요청구분키 / ID / 근거 => 없으면 NA
        [Serailnum] message 80byte 이하 SMS , 초과  LMS
        """

        """
        [messgae]
        req_emp = 5011815
        req_src1 = HSRM
        req_src2 = HSRM
        req_dev = NA

        """
        req_info = self.get_req()
        self.flogger.debug('yd : {}, td: {}, cd: {}, qcd: {}, count:{}'.format(yd, td, cd, qcd, str(len(evt_list))))
        log_str = self.get_log_str()
        for evt in evt_list:
            """
            evt 
                1. 이벤트 발생시간
                2. SAN/STG
                3. 장비 serial
                4. 이벤트 내용\
            evt['event_date'] = evt[0]
            evt['tel_num'] = evt[1]
            evt['dev_serail'] = evt[2]
            evt['dev_alias'] = evt[3]
            evt['dev_vedor'] = evt[4]
            evt['evt_desc'] = evt[5]
            """
            evt_date = evt['event_date']
            evt_dev = evt['dev_type']
            evt_telnum = evt['tel_num']
            evt_serail = evt['dev_alias']
            evt_msg = evt['evt_desc']
            kb_emp = req_info['req_emp']
            app_code = req_info['req_src1']
            pgm_name = req_info['req_src2']
            dev_key  = req_info['req_dev']
            desc ="[{}][{}]{}".format(evt_dev,evt_serail,evt_msg)
            msg="INFO 2 {RCV_NO} {EVT_TIME} {REQ_EMP} P {REQ_SRC1} {REQ_SRC2} {REQ_DEV} {MSG_TXT}".format(
                                                                                    RCV_NO=evt_telnum,
                                                                                    EVT_TIME=evt_date,
                                                                                    REQ_EMP=kb_emp,
                                                                                    REQ_SRC1=app_code,
                                                                                    REQ_SRC2=pgm_name,
                                                                                    REQ_DEV=dev_key,
                                                                                    MSG_TXT=desc)
            if msg in log_str:
                self.flogger.error('dup mag : {}'.format(msg))
            else:
                self.flogger.info(msg)
                self.send(msg)
            self.set_last_seq_no()
        # self.set_cdate()
        self.flogger.info('last seq no :{}'.format(self.last_seq_no))
        print('-'*50)

if __name__=='__main__':
    itsm_event().main()
    # city = u'서울'
    # print(isinstance(city,str))
    # city1=city.encode('utf-8')
    # print(city1)
    # print(isinstance(city1,bytes))
    # print(city1.decode('utf-8'))