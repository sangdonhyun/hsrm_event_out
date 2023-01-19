# -*- coding: cp949 -*-
import re
import datetime
import os
import psycopg2
import configparser

def get_config():
    cfg_file = os.path.join('config','config.cfg')
    cfg = configparser.RawConfigParser()
    cfg.read(cfg_file)
    return cfg

if __name__=='__main__':
    sql="select max(seq_no) from event.event_log"
    cfg = get_config()
    ip=cfg.get('database', 'ip', fallback="121.170.193.217")
    user=cfg.get('database', 'user', fallback="webuser")
    dbname=cfg.get('database', 'dbname', fallback="qweb")
    password=cfg.get('database', 'password', fallback="qw19850802@")

    conn_str="host='{}' dbname='{}' user='{}' password='{}'".format(ip,dbname,user,password)

    db = psycopg2.connect(conn_str)
    cursor = db.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    print('last seq no :',rows[0][0])
    if len(rows) > 0:
        with open(os.path.join('config','seq_no.txt'),'w') as fw:
            fw.write(str(rows[0][0]))


