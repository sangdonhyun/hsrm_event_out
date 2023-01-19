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
import kb_one_cloud

class kb_onecloud_event():
    def __init__(self):
        self.now = datetime.datetime.now()
        self.flogger = self.get_logger
        self.cfg = self.get_cfg()
        self.c_file = os.path.join('config','c_date.txt')
        self.fc = fleta_crypto.AESCipher('kes2719!')
        self.conn_string = self.get_conn_str()
        self.kb_one = kb_one_cloud.event()
        self.last_seq_no = self.get_last_seq_no()
        self.seq_file = os.path.join('config','seq_no.txt')


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
                fw.write(self.last_seq_no)


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
        cfg.read(cfg_file)
        return cfg

    def get_url(self):
        ip = self.cfg.get('kb_one_cloud', 'ip')
        port = self.cfg.get('kb_one_cloud', 'port')
        url = self.cfg.get('kb_one_cloud', 'url')
        token = self.cfg.get('kb_one_cloud', 'token')
        if url[:1] == '/':
            url = url[1:]
        http_str =  'http://{}:{}/{}'.format(ip,port,url)
        return http_str

    def get_curl_cmd(self):
        token  = self.cfg.get('kb_one_cloud','token')
        http_str = self.get_url()
        cmd = """curl -v -H "Accept: application/json" -H "Authorization:   Basic {TOKEN} " -H "Content-Type: application/json" -X POST -d@send.json "{URL}" """.format(TOKEN=token,URL=http_str)
        # cmd = """curl -v -H "Accept: application/json" -user "mid.event.integration:Kbsnevt0905@!" -H "Content-Type: application/json" -X POST -d@send.json "{URL}" """.format(TOKEN=token,URL=http_str)
        return cmd


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
        q = q.replace('{LAST_SEQ_NO}',self.last_seq_no)
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
        #for evt in q_list:
        evt_arg_list, evt_list = list(),list()
        # for evt in q_list:
        for evt in q_list[-3:]:
            evt_arg_info = dict()
            evt_info = dict()
            for i in range(len(evt)):
                arg_num = i+1
                arg_msg = evt[i]
                if arg_msg == None:
                    arg_msg="None"
                evt_arg_info['arg_{}'.format(str(arg_num))] = arg_msg.strip()

            # evt_info = dict()
            # date_str = datetime.datetime.strftime(datetime.datetime.strptime(evt[0],'%Y-%m-%d %H:%M:%S'),'%Y%m%d%H%M%S')
            # evt_info['event_date']    = date_str
            # evt_info['serial_number'] = evt[1]
            # evt_info['event_code']    = evt[2]
            # evt_info['event_level']   = evt[3]
            # evt_info['q_event_level'] = evt[4]
            # evt_info['desc_summary']  = evt[5]
            """
            event_date, 0
            serial_number,1
            event_code,2
            event_level,3
            q_event_level ,4
            device_type ,5
            al.device_alias,6
            desc_summary7
            """
            print(evt)
            date_str = datetime.datetime.strftime(datetime.datetime.strptime(evt[0],'%Y-%m-%d %H:%M:%S'),'%Y%m%d%H%M%S')
            evt_info['description'] = ''
            evt_info['source'] = 'HSRM'
            evt_info['type'] = evt[5]
            evt_info['message_key'] = evt[5].strip() + date_str
            evt_info['time_of_event'] = evt[0]

            if evt[4].strip() == 'Critical':
                evt_info['severity'] = '5'
            elif evt[4].strip() == 'Warnning':
                evt_info['severity'] = '4'
            else:
                evt_info['severity'] = '0'


            evt_info['node'] = evt[1]
            evt_info['resource'] = evt[6]
            # evt_info['state'] = 'New'
            evt_info['resolution_state'] = ''
            print(evt[4].strip())
            print(evt_info['resource'])

            date_str = datetime.datetime.strftime(datetime.datetime.strptime(evt[0], '%Y-%m-%d %H:%M:%S'),
                                                  '%Y%m%d%H%M%S')

            evt_list.append(evt_info)
            evt_arg_list.append(evt_arg_info)
            self.self.last_seq_no = evt[-1]
        return evt_arg_list, evt_list

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

    def get_arg_set(self,msg_format):
        fd=re.findall('\{\d\}',msg_format)
        return fd



    def main(self):
        yd_date = self.now - datetime.timedelta(days=1)
        yd = yd_date.strftime('%Y-%m-%d')
        td = self.now.strftime('%Y-%m-%d')
        qcd,cd = self.get_cdate()
        evt_arg_list, evt_list = self.get_evt_list(yd, td, qcd)

        print('event count :',len(evt_list))
        log_str = self.get_log_str()
        swi_msg_bit = False
        swi_msg = str()
        # evt_list = list()
        for i in range(len(evt_arg_list)):
            evt_arg_info = evt_arg_list[i]
            evt_info = evt_list[i]
            print('evt_arg_info :', evt_arg_info)

            event_format = self.cfg.get('common', 'msg_format', fallback='[{1}][{2}][{3}][{5}][{6}]')
            msg = event_format
            fd = re.findall('\{\d\}', msg)
            for arg in fd:
                arg_num = re.search('\d',arg).group()
                evt_arg = 'arg_{}'.format(arg_num)
                tg_msg = evt_arg_info[evt_arg]
                msg = msg.replace(arg,tg_msg)
                if len(re.findall('\[',tg_msg)) > 2:
                    swi_msg_bit = True
                    swi_msg = tg_msg
            if swi_msg_bit :
                msg = swi_msg
            evt_info['description'] = msg.strip()
            evt_list.append(evt_info)
            # if msg in log_str:
            #     self.flogger.error('dup mag : {}'.format(msg))
            # else:
            #     self.flogger.info(msg)
            #     self.send_file(msg)
        # self.set_cdate()

        event_data_list = self.kb_one.get_event_list_data(evt_list)
        print('-'*40)
        print('-'*40)
        print(event_data_list)
        print('-' * 40)
        print('-' * 40)
        with open('send.json','w') as fw:
            fw.write(json.dumps(event_data_list,indent=4))
        if len(evt_list) > 0:
            cmd  = self.get_curl_cmd()
            print(cmd)
            ret=os.popen(cmd).read()
            print(ret)
            self.flogger.info(ret)
            self.set_last_seq_no()

        else:
            self.flogger.info('count : 0')
        print('-'*50)

if __name__=='__main__':
    ev = kb_onecloud_event()
    print(ev.get_url())
    print(ev.get_curl_cmd())
    ev.main()

    # city = u'서울'
    # print(isinstance(city,str))
    # city1=city.encode('utf-8')
    # print(city1)
    # print(isinstance(city1,bytes))
    # print(city1.decode('utf-8'))