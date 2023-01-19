from pysnmp.hlapi import *
import configparser
import os
import re

class trap_send():
    def __init__(self, msg_info=dict()):
        self.msg_info = msg_info
        self.snmp_cfg = self.get_cfg()

    def get_cfg(self):
        cfg = configparser.RawConfigParser()
        cfg_file = os.path.join('config','snmp.cfg')
        cfg.read(cfg_file,encoding='utf-8')
        return cfg

    def fwrite(self, msg, wbit='a'):
        with open('input.txt',wbit) as fw:
            fw.write(msg+'\n')

    def set_msg(self,msg):
        if '{' in msg:
            str_pre = msg[:msg.index('{')]
            st_num = msg.index('{')
            ed_num = msg.index('}')
            m_str = msg[st_num+1:ed_num]
            for key in self.msg_info.keys():
                if key in m_str:
                    if 'DATA' in key and ':' in key:
                        m_str = self.msg_info['DATE']
                    elif 'TIME' in key and ':' in key:
                        m_str = self.msg_info['TIME']
                    else:
                        m_str = self.msg_info[key]
            m_str = str_pre+m_str
        else:
            m_str = msg
        print('m_str :',m_str)
        return m_str

    def make_input_file(self):
        opts = self.snmp_cfg.options('snmp')
        self.fwrite('inform', 'w')
        for opt in opts:
            msg = self.snmp_cfg.get('snmp', opt)
            msg = self.set_msg(msg)
            if not re.search('^v', opt):
                self.fwrite('-{} {}'.format(opt, msg))
            else:
                self.fwrite('-v {}'.format(msg))

    def send(self):
        self.make_input_file()
        cmd = 'trapgen -f input.txt'
        ret=os.popen(cmd).read()
        print(ret)

if __name__=='__main__':
    snmp_dict = dict()
    snmp_dict['DATE'] = '2022/01/16'
    snmp_dict['TIME'] = '12:10:00'
    snmp_dict['MSG'] = 'This is test code '
    snmp_dict['SERIAL'] = '12345'

    trap_send(snmp_dict).send()