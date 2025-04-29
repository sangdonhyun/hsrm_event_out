import logging
from logging.handlers import TimedRotatingFileHandler
msg = "HSRM_warning syslog test"
hsrm_logger = logging.getLogger('hsrmlogger')
#my_logger.setLevel(logging.INFO)
hsrm_logger.setLevel(logging.WARN)
handler = logging.handlers.SysLogHandler(address = ('121.170.193.203',514))
hsrm_logger.addHandler(handler)
print(msg)
hsrm_logger.warning(msg)

#
# syslog_ip = '121.170.193.203'
# syslogger = logging.getLogger('HSRM_critical')
# syslogger.setLevel(logging.CRITICAL)
# handler = logging.handlers.SysLogHandler(address=(syslog_ip, 514),
#                                          facility=19)
# syslogger.addHandler(handler)
# print(msg)
# syslogger.error(msg)