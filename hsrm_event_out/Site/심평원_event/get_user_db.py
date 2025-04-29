import os
import psycopg2
import configparser

class userdb():
    def __init__(self):

        self.cfg = self.getCfg()
        self.conn_string = self.getConnStr()
        print(self.conn_string)

    def getCfg(self):
        cfg = configparser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg

    def getConnStr(self):
        ip = self.cfg.get('userdb','ip',fallback='localhost')
        user = self.cfg.get('userdb','user',fallback='webuser')
        dbname = self.cfg.get('userdb','dbname',fallback='qweb')
        passwd = self.cfg.get('userdb','password',fallback='qw19850802@')
        port = self.cfg.get('userdb','port',fallback='5432')
        return "host='%s' dbname='%s' user='%s' password='%s' port='%s'"%(ip,dbname,user,passwd,port)

    def get_row(self, query_string):
        db = psycopg2.connect(self.conn_string)
        cursor = db.cursor()
        cursor.execute(query_string)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    def get_user_list(self):
        query = """
        SELECT user_id, user_pwd, user_name, department, email, cellphone, local_phone, auth_id, account_create_date, ip_addr, use_yn, "token", theme, selected_work_div, mod_dt, system_dashboard, interval_dashboard, selected_evt_lvl, layout, before_passwords, login_try_count, system_account_yn, beep_sound_yn
FROM web.web_user_info;
            """
        user_list = self.get_row(query)
        return user_list

    def main(self):
        user_list = self.get_user_list()
        for user in user_list:
            print(user)
if __name__=='__main__':
    userdb().main()