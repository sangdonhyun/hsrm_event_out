import configparser
import os
import datetime
import glob

class log_manager():
    def __init__(self):
        self.cfg = self.get_cfg()

    def get_cfg(self):
        cfg = configparser.RawConfigParser()
        cfg_file = os.path.join('config','config.cfg')
        cfg.read(cfg_file)
        return cfg

    def get_last_month(self):
        today = datetime.date.today()
        first = today.replace(day=1)
        last_month = first - datetime.timedelta(days=1)
        print(last_month.strftime("%Y%m"))
        return last_month.strftime("%Y%m")

    def del_local_log(self):
        clear_day = self.cfg.get('log','clear_day',fallback=30)
        n=datetime.datetime.now()
        old_log_date = n - datetime.timedelta(days=int(clear_day))
        old_log_str = old_log_date.strftime('%Y%m%d')
        log_list = glob.glob(os.path.join('Site/hanhwa/config/logs', '*.log'))
        for log_name in log_list:
            log_date_str = os.path.splitext(os.path.basename(log_name))[0]
            print(log_date_str, old_log_str, log_date_str < old_log_str)
            if log_date_str < old_log_str:
                os.remove(log_name)

    def month_log_clear(self):
        log_file_name = self.cfg.get('common','event_file')
        last_month = self.get_last_month()
        if os.path.isfile(log_file_name):
            backup_file_name = log_file_name+'.{}'.format(last_month)
            if os.path.isfile(backup_file_name):
                os.rename(backup_file_name,backup_file_name+'.'+datetime.datetime.now().strftime('%y%m%d%H%M%S'))
            print('make file :',backup_file_name)
            os.rename(log_file_name,backup_file_name)

    def main(self):
        self.del_local_log()
        self.month_log_clear()

if __name__=='__main__':
    log_manager().main()
