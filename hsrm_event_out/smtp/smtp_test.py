# -*- coding:utf-8 -*-

import smtplib
import ssl
from email.mime.text import MIMEText
import datetime
"""
muse@fletacom.com
smtp.cafe24.com
587

godmuse01@gmail.com
smtp.cafe24.com
587

godmuse01@naver.com
smtp.naver.com
587
"""




smtp_host = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'godmuse01@gmail.com'
smtp_passwd = 'tkdehs#0013'
smtp_passwd = 'kajqwzxfrqowdwot'
target_user = 'muse@fletacom.com;godmuse@daum.net;godmuse01@naver.com;hsyoo@fletacom.com'
# target_user = 'godmuse01@naver.com'
#target_user = 'godmuse01@naver.com'
now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
user_list = list()
if ';' in target_user:
    for user in target_user.split(';'):
        user_list.append(user)
else:
    user_list.append(target_user)
msg_content = '메세지 테스트 {DT} [Critical][STG][스토리지 #000427(00000000000297000427)][Symmetrix 000292605459 : Component state has changed to Offline. - Object is: 000292605459:DB-1B/ENC-2/LCC-B]'.format(DT=now)

msg = MIMEText(msg_content)
msg['Subject'] = '[HSRM]{DT} STG Event test2'.format(DT=now)
msg['From'] = 'HSRM<{SMTP_USER}>'.format(SMTP_USER=smtp_user)
# msg['From'] = smtp_user
#msg['To'] = user

smtp = smtplib.SMTP(smtp_host, 587)
smtp.ehlo()  # say Hello
smtp.starttls()  # TLS 사용시 필요
smtp.login(smtp_user, smtp_passwd)
# msg = MIMEText(msg_content)
# msg['Subject'] = '[HSRM] STG Event test'
# msg['To'] = smtp_user
# for user in user_list:
#     msg['To'] = user
    #print(user)
    #smtp.sendmail(smtp_user, user, msg.as_string())
    #print(msg)
msg['To'] = ','.join(user_list)
smtp.sendmail(smtp_user, msg['To'].split(','), msg.as_string())
print(msg.as_string())
smtp.quit()

print(type(msg))
print(dir(msg))

# context = ssl.create_default_context()
# with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
#     server.login(smtp_user, smtp_passwd)
#     server.sendmail(smtp_user, target_user, msg.as_string())