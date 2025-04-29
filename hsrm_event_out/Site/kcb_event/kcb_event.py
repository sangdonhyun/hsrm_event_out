'''
Created on 2012. 10. 12.
Modify on 2023-01-16
@author: muse
현재 시간 기준 마지막 쿼리 시간 부터 => lost seq_no 이후 로 쿼리 수정.
kcb_event :
passowrd 암호화
event send --> snmp
'''

import psycopg2
import datetime
import socket
import json
import sys
import configparser
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import re
import fleta_crypto
import fleta_snmp
import smtplib
import ssl
from email.mime.text import MIMEText


class itsm_event():
    def __init__(self):
        self.now = datetime.datetime.now()
        self.seq_file = os.path.join('config','seq_no.txt')
        self.seq_no = self.get_seq_no()
        self.flogger = self.get_logger
        self.cfg = self.get_cfg()
        self.c_file = os.path.join('config','c_date.txt')
        self.fc = fleta_crypto.AESCipher('kes2719!')
        self.conn_string = self.get_conn_str()
        print(self.conn_string)


    def get_seq_no(self):

        if not os.path.isfile(self.seq_file):
            self.set_seq_no('1')
        with open(self.seq_file) as f:
            seq_no = f.read()
        return seq_no

    def set_seq_no(self,seq_no):
        with open(self.seq_file,'w') as fw:
            fw.write(str(seq_no))


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
        log_file = os.path.join('logs', self.now.strftime('%Y%m%d.log'))
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(u'%(asctime)s %(levelname)s ==> %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger




    def get_conn_str(self):
        ip = self.cfg.get('database', 'ip', fallback='localhost')
        user = self.cfg.get('database', 'user', fallback='webuser')
        dbname = self.cfg.get('database', 'dbname', fallback='qweb')
        passwd = self.cfg.get('database', 'password', fallback='qw19850802@')
        port = self.cfg.get('database', 'port', fallback='5432')
        if len(passwd) > 20:
            passwd = self.fc.decrypt(passwd)
            if isinstance(passwd, bytes):
                passwd = passwd.decode('utf-8')
        return "host='%s' dbname='%s' user='%s' password='%s' port='%s'" % (ip, dbname, user, passwd, port)

    def get_cfg(self):
        cfg = configparser.RawConfigParser()
        cfg_file = os.path.join('config','config.cfg')
        print(cfg_file,os.path.isfile(cfg_file))
        cfg.read(cfg_file)
        print(cfg.sections())
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

    def send_syslog(self,level,msg):
        if level == 'Critical':
            log_level = logging.ERROR
        elif level == 'Warning':
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        syslog_server_list= list()
        for opt in self.cfg.options('server'):
            if 'syslog_ip' in opt :
                syslog_server_list.append(self.cfg.get('server', opt))

        for syslog_ip in syslog_server_list:
            # syslog_ip = self.cfg.get('server','syslog_ip', fallback='localhost')
            hsrm_logger = logging.getLogger('hsrmlogger')
            # my_logger.setLevel(logging.INFO)

            hsrm_logger.setLevel(log_level)
            handler = logging.handlers.SysLogHandler(address=(syslog_ip, 514))
            hsrm_logger.addHandler(handler)
            print('syslog_ip :', syslog_ip)
            print(msg)
            if level == 'Critical':
                hsrm_logger.error(msg)
            elif level == 'Warning':
                hsrm_logger.warning(msg)
            else:
                hsrm_logger.info(msg)


    def send_snmp(self, evt_info, msg):
        """
        #1: event_date yyyy-mm-dd HH:MM:SS
        #2: serial_number
        #3: event_code
        #4: event_level , vender event level
        #5: q_event_level , hsrm event level
        #6: device_type
        #7: device_alias
        #8: desc_summary

        snmp_dict['DATE'] = '2022/01/16'
        snmp_dict['TIME'] = '12:10:00'
        snmp_dict['MSG'] = 'This is test code '
        snmp_dict['SERIAL'] = '12345'

        """
        print(msg)
        print(evt_info)

        datetime_str = evt_info['arg_1']
        print('datetime_str :',datetime_str.strip(),len(datetime_str))
        dt = datetime.datetime.strptime(datetime_str.strip(), '%Y-%m-%d %H:%M:%S')
        print(dt,type(dt))
        date_str  = dt.strftime('%Y/%m/%d')
        time_str  = dt.strftime('%H:%M:%S')
        serial = evt_info['arg_2']
        snmp_dict = dict()
        snmp_dict['DATE'] = date_str
        snmp_dict['TIME'] = time_str
        snmp_dict['SERIAL'] = serial
        snmp_dict['MSG'] = msg
        fleta_snmp.trap_send(snmp_dict).send()

    def send_smtp_nomal(self,msg_content):
        smtp_host = self.cfg.get('smtp', 'smtp_host', fallback='smtp.fletacom.com')
        smtp_user = self.cfg.get('smtp', 'smtp_user', fallback='fleta@fletacom.com')
        smtp_passwd = self.cfg.get('smtp', 'smtp_passwd', fallback='fleta123')
        target_user = self.cfg.get('smtp', 'target_user', fallback='fleta@fletacom.com')
        smtp_title = self.cfg.get('smtp', 'smtp_title', fallback='[HSRM] Event Message')
        smtp_port = self.cfg.get('smtp', 'smtp_port', fallback='25')

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_list = list()
        if ';' in target_user:
            for user in target_user.split(';'):
                user_list.append(user)
        else:
            user_list.append(target_user)


        msg = MIMEText(msg_content)
        msg['Subject'] = smtp_title
        msg['From'] = 'HSRM<{SMTP_USER}>'.format(SMTP_USER=smtp_user)

        smtp = smtplib.SMTP(smtp_host, 25)
        msg['To'] = ','.join(user_list)
        smtp.sendmail(smtp_user, msg['To'].split(','), msg.as_string())
        print(msg.as_string())
        smtp.quit()



    def send_smtp_ssl(self,msg_content):
        smtp_host = self.cfg.get('smtp', 'smtp_host', fallback='smtp.fletacom.com')
        smtp_user = self.cfg.get('smtp', 'smtp_user', fallback='fleta@fletacom.com')
        smtp_passwd = self.cfg.get('smtp', 'smtp_passwd', fallback='fleta123')
        target_users = self.cfg.get('smtp', 'target_user', fallback='fleta@fletacom.com')
        smtp_title = self.cfg.get('smtp', 'smtp_title', fallback='[HSRM] Event Message')
        smtp_port = self.cfg.get('smtp', 'smtp_port', fallback='465')

        msg = MIMEText(msg_content)
        msg['Subject'] = smtp_title
        msg['To'] = smtp_user

        context = ssl.create_default_context()
        user_list = list()
        if ';' in target_users:
            for user in target_users.split(';'):
                user_list.append(user)
        else:
            user_list.append(target_users)
        for user in user_list:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                server.login(smtp_user, smtp_passwd)
                server.sendmail(smtp_user, user, msg.as_string())


    def send_smtp_tcl(self,msg_content):
        smtp_host = self.cfg.get('smtp', 'smtp_host', fallback='smtp.fletacom.com')
        smtp_user = self.cfg.get('smtp', 'smtp_user', fallback='fleta@fletacom.com')
        smtp_passwd = self.cfg.get('smtp', 'smtp_passwd', fallback='fleta123')
        target_users = self.cfg.get('smtp', 'target_user', fallback='fleta@fletacom.com')
        smtp_title = self.cfg.get('smtp', 'smtp_title', fallback='[HSRM] Event Message')
        smtp_port = self.cfg.get('smtp', 'smtp_port', fallback='587')
        msg = MIMEText(msg_content)
        msg['Subject'] = smtp_title
        msg['To'] = smtp_user
        print('smtp_port :',smtp_port,type(smtp_port))
        smtp = smtplib.SMTP(smtp_host, int(smtp_port))
        smtp.ehlo()  # say Hello
        smtp.starttls()  # TLS 사용시 필요
        smtp.login(smtp_user, smtp_passwd)
        user_list = list()
        if ';' in target_users:
            for user in target_users.split(';'):
                user_list.append(user)
        else:
            user_list.append(target_users)

        for user in user_list:
            smtp.sendmail(smtp_user, user, msg.as_string())
            print(msg.as_string())
        smtp.quit()


    def send_smtp(self,msg_content):
        smtp_method = self.cfg.get('smtp', 'smtp_method', fallback='')
        if smtp_method == 'tcl':
            self.send_smtp_tcl(msg_content)
        elif smtp_method== 'ssl':
            self.send_smtp_ssl(msg_content)
        else:
            self.send_smtp_nomal(msg_content)

    def send_file(self,msg):
        event_file = self.cfg.get('common','event_file')
        try:
            with open(event_file,'a') as fw:
                fw.write(msg)
                fw.write('\n')
        except Exception as e:
            self.flogger.error(str(e))
            print(str(e))

    def send_socket(self,msg):
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
            q = q.replace('{SEQ_NO}',self.seq_no)
        print(q)
        q_list = self.getRaw(q)
        """
        2022-03-04 09:20:55	01077778888	00000000000000011015	411015	STG	HITACHI	is a Error test code.[PORT:5E]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        2022-03-15 10:35:55	01077778888	00000000000000011536	11536	STG	HITACHI	is a Error test code.[PORT:5E]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        2022-03-15 10:35:55	01077778888	00000000000000011537	11537	STG	HITACHI	is a Error test code.[PORT:5E]
        """
        """
        event_date,
        serial_number,
        event_code,
        event_level,
        q_event_level ,
        desc_summary
        """

        for evt in q_list:
            evt_info = dict()
            for i in range(len(evt)):
                arg_num = i+1
                arg_msg = evt[i]
                if arg_msg == None:
                    arg_msg="None"
                evt_info['arg_{}'.format(str(arg_num))] = str(arg_msg).strip()
                seq_no = evt[-1]
            # evt_info = dict()
            # date_str = datetime.datetime.strftime(datetime.datetime.strptime(evt[0],'%Y-%m-%d %H:%M:%S'),'%Y%m%d%H%M%S')
            # evt_info['event_date']    = date_str
            # evt_info['serial_number'] = evt[1]
            # evt_info['event_code']    = evt[2]
            # evt_info['event_level']   = evt[3]
            # evt_info['q_event_level'] = evt[4]
            # evt_info['desc_summary']  = evt[5]
            evt_list.append(evt_info)
        if len(q_list) > 0:
            self.set_seq_no(seq_no)
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
        log_file = os.path.join('logs', self.now.strftime('%Y%m%d.log'))
        with open(log_file) as f:
            log_str = f.read()
        return log_str

    def get_arg_set(self,msg_format):
        fd=re.findall('\{\d\}',msg_format)
        return fd



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
        # req_info = self.get_req()
        self.flogger.debug('yd : {}, td: {}, cd: {}, qcd: {}, count:{}'.format(yd, td, cd, qcd, str(len(evt_list))))
        log_str = self.get_log_str()
        swi_msg_bit = False
        swi_msg = str()
        for evt_info in evt_list:
            print(evt_info)
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
            event_format = self.cfg.get('common', 'msg_format', fallback='[{1}][{2}][{3}][{5}][{6}]')
            msg = event_format

            # print('format :',msg)
            # print(evt_info)
            fd = re.findall('\{\d\}', msg)
            print(fd)
            for arg in fd:
                arg_num = re.search('\d',arg).group()
                evt_arg = 'arg_{}'.format(arg_num)
                tg_msg = str(evt_info[evt_arg]).strip()
                msg = msg.replace(arg,tg_msg)
                if len(re.findall('\[',tg_msg)) > 2:
                    swi_msg_bit = True
                    swi_msg = tg_msg
            # print(evt_info['event_date'])
            # msg = msg.replace('{1}', evt_info['event_date'])
            # print(msg)
            # msg = msg.replace('{2}', evt_info['serial_number'].strip())
            # msg = msg.replace('{3}', evt_info['event_code'].strip())
            # msg = msg.replace('{4}', evt_info['event_level'].strip())
            # msg = msg.replace('{5}', evt_info['q_event_level'].strip())
            # msg = msg.replace('{6}', evt_info['desc_summary'].strip())

            if swi_msg_bit :
                msg = swi_msg
            print(msg)
            if msg in log_str:
                self.flogger.error('dup mag : {}'.format(msg))
            else:
                self.flogger.info(msg)
                send_method = self.cfg.get('common', 'event_method', fallback='file')
                if send_method == 'syslog':
                    self.send_syslog(evt_info['arg_5'], msg)
                elif send_method == 'snmp':
                    self.send_snmp( msg)
                elif send_method == 'smtp':
                    self.send_smtp( msg)
                else:
                    self.send_file(msg)

        # self.set_cdate()
        print('-'*50)

if __name__=='__main__':
    itsm_event().main()
    # city = u'서울'
    # print(isinstance(city,str))
    # city1=city.encode('utf-8')
    # print(city1)
    # print(isinstance(city1,bytes))
    # print(city1.decode('utf-8'))