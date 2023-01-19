
import psycopg2
import datetime
import socket
import json
import sys
import configparser
import os
import logging
import re


class itsm_event():
    def __init__(self):
        self.now = datetime.datetime.now()
        self.flogger = self.get_logger()
        self.cfg = self.get_cfg()
        self.conn_string = self.get_conn_str()
        # print(self.conn_string)
        self.c_file = os.path.join('config','c_date.txt')
        self.last_seq_no = self.get_seq_no()

    def set_seq_no(self,seq_no):
        self.flogger.info('set last seq_no :{}'.format(seq_no))
        seq_file = os.path.join('config', 'seq_no.txt')
        with open(seq_file) as fw:
            fw.write(str(seq_no))

    def get_seq_no(self):
        seq_file = os.path.join('config','seq_no.txt')
        with open(seq_file) as f:
            seq_no = f.read()
        return seq_no

    def get_logger(self):
        if not os.path.isdir('logs'):
            os.makedirs('logs')
        formatter = logging.Formatter('%(asctime)s %(lineno)d %(levelname)s ==>%(message)s')
        #logging.basicConfig(format='%(asctime)s %(lineno)d %(levelname)s:%(message)s', level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        stream_hander = logging.StreamHandler()
        stream_hander.setFormatter(formatter)
        logger.addHandler(stream_hander)
        log_file = os.path.join('logs',self.now.strftime('%Y%m%d.log'))
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(lineno)d %(levelname)s ==>%(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    def get_conn_str(self):
        ip = self.cfg.get('database','ip')
        user = self.cfg.get('database','user')
        dbname = self.cfg.get('database','dbname')
        password = self.cfg.get('database','password')
        port = self.cfg.get('database','port')
        return "host='{}' dbname='{}' user='{}' password='{}' port ='{}'".format(ip,dbname,user,password,port)

    def get_cfg(self):
        cfg = configparser.RawConfigParser()
        cfg_file = os.path.join('config','config.cfg')
        cfg.read(cfg_file)
        return cfg

    def getRaw(self, query_string):
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
            #if isinstance(msg,str):
            msg=msg.encode('euc-kr')
            #print(msg)
            sock.sendall(msg)
        except socket.error as e:
            self.flogger.error(str(e))
        finally:
            sock.close()

    def get_evt_list(self,yd,td,qcd,cd):
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
        q = q.replace('{CD}',qcd)
        if '{SEQ_NO}' in q:
            q = q.replace('{SEQ_NO}', self.last_seq_no)
        print(q)
        q_list = self.getRaw(q)
        
        """
        2022-03-04 09:20:55	01077778888	00000000000000011015	411015	STG	HITACHI	is a Error test code.[PORT:5E]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        2022-03-15 10:35:55	01077778888	00000000000000011536	11536	STG	HITACHI	is a Error test code.[PORT:5E]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        2022-03-15 10:35:55	01077778888	00000000000000011537	11537	STG	HITACHI	is a Error test code.[PORT:5E]
        """
        """
event_date ,
       telephone,
       serial_number dev_serial,
       view.device_alias_zero(serial_number) dev_alias,
       device_type ,
       vendor_name ,
       desc_summary
       """
        """
event_date ,
       telephone,
       event.device_uid_zero(serial_number) dev_serial,
       event.device_alias_zero(serial_number) dev_alias,
       device_type ,
       vendor_name ,
       event_code,
       event_level,     
       q_event_level,   
       desc_summary
"""
       
        for evt in q_list:
            print(evt)
            evt_info = dict()
            date_str = datetime.datetime.strftime(datetime.datetime.strptime(evt[0],'%Y-%m-%d %H:%M:%S'),'%Y%m%d%H%M%S')
            evt_info['event_date'] = date_str
            evt_info['tel_num'] = evt[1]
            evt_info['dev_serail'] = evt[2]
            evt_info['dev_alias'] = evt[3]
            evt_info['dev_type'] = evt[4]
            evt_info['dev_vedor'] = evt[5]
            evt_info['event_code'] = evt[6]
            evt_info['event_level'] = evt[7]
            evt_info['evt_desc'] = evt[8]
            seq_no = evt[-1]

            evt_list.append(evt_info)
        if len(q_list) > 0:
            self.set_seq_no(seq_no)
        return evt_list

    def get_req(self):
        req_info = dict()
        for opt in self.cfg.options('message'):
            req_info[opt] = self.cfg.get('message',opt)
        return req_info

    def get_cdate(self):
        cd = self.now - datetime.timedelta(days=1)
        cdate = cd.strftime('%Y-%m-%d %H:%M:%S')
        if os.path.isfile(self.c_file):
            with open(self.c_file) as f:
                cdate = f.read()
        self.set_cdate()
        cdate_dt = datetime.datetime.strptime(cdate,'%Y-%m-%d %H:%M:%S')
        cdate_1min = cdate_dt - datetime.timedelta(minutes=1)
        cdate_str = cdate_1min.strftime('%Y-%m-%d %H:%M:%S')
        return cdate,cdate_str

    def set_cdate(self):
        with open(self.c_file,'w') as fw:
            fw.write(self.now.strftime('%Y-%m-%d %H:%M:%S'))
        print('check date  : ',self.now.strftime('%Y-%m-%d %H:%M:%S'))
    def main(self):

        yd_date = self.now - datetime.timedelta(days=1)
        yd = yd_date.strftime('%Y-%m-%d')
        td = self.now.strftime('%Y-%m-%d')
        cd,qcd = self.get_cdate()
        print(qcd,cd)
        evt_list = self.get_evt_list(yd, td, qcd,cd)
        print('event count :',len(evt_list))
        """
      
        """

        """
        [messgae]
        req_emp = 5011815
        req_src1 = HSRM
        req_src2 = HSRM
        req_dev = NA

        """
        req_info = self.get_req()
        self.flogger.debug('YD[{}], TD[{}], QCD[{}], CD[{}], count : {}'.format(yd,td,qcd,cd,str(len(evt_list))))
        for evt in evt_list:
            """
          
             
            evt['event_date'] = evt[0]
            evt['tel_num'] = evt[1]
            evt['dev_serail'] = evt[2]
            evt['dev_alias'] = evt[3]
            evt['dev_vedor'] = evt[4]
            evt['evt_desc'] = evt[5]


       event_date ,
       telephone,
       event.device_uid_zero(serial_number) dev_serial,
       event.device_alias_zero(serial_number) dev_alias,
       device_type ,
       vendor_name ,
       event_code,
       
       desc_summary

       
            """
            evt_date = evt['event_date']
            evt_dev = evt['dev_type']
            evt_telnum = evt['tel_num']
            evt_serial = evt['dev_alias']
            evt_msg = evt['evt_desc'].strip()
            kb_emp = req_info['req_emp']
            app_code = req_info['req_src1']
            pgm_name = req_info['req_src2']
            dev_key  = req_info['req_dev']
            event_level  = evt['event_level'].strip()
            event_code  = evt['event_code'].strip()
            print("evt_msg :",evt_msg)
            desc ="[{VENDOR_LEVEL}][{ALIAS}][{CODE}]{MSG}".format(VENDOR_LEVEL=event_level,ALIAS=evt_serial,CODE=event_code,MSG=evt_msg)
            print("desc :",desc)
            msg="INFO 2 {RCV_NO} {EVT_TIME} {REQ_EMP} P {REQ_SRC1} {REQ_SRC2} {REQ_DEV} {MSG_TXT}".format(
                                                                                    RCV_NO=evt_telnum,
                                                                                    EVT_TIME=evt_date,
                                                                                    REQ_EMP=kb_emp,
                                                                                    REQ_SRC1=app_code,
                                                                                    REQ_SRC2=pgm_name,
                                                                                    REQ_DEV=dev_key,
                                                                                    MSG_TXT=desc)
            print(msg)
            			
            
            #now = datetime.datetime.now()
            log_file = os.path.join('logs',self.now.strftime('%Y%m%d.log'))  
            with open(log_file) as f:
                log_str = f.read()
            print(type(log_str),len(log_str))
            print(type(msg),len(msg))			
            msg = msg.replace('-','')
            log_str = log_str.replace('-','')
            
            if  msg in log_str:
                self.flogger.info('dup msg  :'+msg)
            else:
                self.flogger.info(msg)
                self.send(msg)
        #self.set_cdate()
        print('-'*50)

if __name__=='__main__':
    itsm_event().main()

    # print(isinstance(city,str))
    # city1=city.encode('utf-8')
    # print(city1)
    # print(isinstance(city1,bytes))
    # print(city1.decode('utf-8'))
