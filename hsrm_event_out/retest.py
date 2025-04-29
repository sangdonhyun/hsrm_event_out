import re
# a="[{1}][{2}] {3} {5} {6}"
#
# aa=re.findall('\{\d\}',a)
# print (aa)
#
#
# for arg in aa:
#
#     arg=arg.replace('}','')
#     arg=arg.replace('{','')
#     print(re.search('\d',arg).group())
#


# bb='[2022-09-30 00:02:25][00000000001002ALJ5EM][SWI.MON.SFP.RX.I4][Warning][[2022-09-30 00:02:25][Warning][SFP RX][N/A (1002ALJ5EM)][Index:4,Slot:N/A,Port:4] SFP Rx Power 461.2uW [Port Speed:8, Threshold:500uW], Linked Devices : [SVR] FLETA-ESXI1,FLETA-ESXI2  [STG] 200A0828B1A(N/A)]'
# msg_format = "[{1}][{2}][{3}][{5}][{6}]"

#
# print(re.findall('\[',bb))
#
# print(re.compile('\[a-z\]' ,bb))


# remove_text = 'asdf(asdf)'
# print(remove_text)
# print(re.sub(r'\([^)]*\)', '', remove_text))
#
#
# remove_text = 'asdf<asdf>'
# print(remove_text)
# print(re.sub(r'\<[^>]*\>', '', remove_text))
#
# aa= re.compile(r'\<[^>]*\>')
#
# import re
# str ="LOG_ADD(LOG_FLOAT, [actuator]Thrust, [&a]ctuatorThrust)"
# items = re.findall('\(([^)]+)', str)   #extracts string in bracket()
# print (items)
# items = re.findall('\[([^]]+)', str)   #extracts string in bracket()
# print (items)
#
#
# regex = r"'\[([^]]+)'"
#
# text = re.sub('\[([^]]+)','', bb)
# print('-'*50)
# print(text)
# text = text.replace(']','')
# text = text.replace('[','')
# print(text)

## 정규식 이용
# p = re.compile(r"\[(.+)\](.+)")
# m = p.match(bb)
# print(m.groups())


#
# bb='[2022-09-30 00:02:25][00000000001002ALJ5EM][SWI.MON.SFP.RX.I4][Warning][[2022-09-30 00:02:25][Warning][SFP RX][N/A (1002ALJ5EM)][Index:4,Slot:N/A,Port:4] SFP Rx Power 461.2uW [Port Speed:8, Threshold:500uW], Linked Devices : [SVR] FLETA-ESXI1,FLETA-ESXI2  [STG] 200A0828B1A(N/A)]'
# items = re.findall('\[([^]]+)', bb)
# print(items)
#
# for item in items:
#     print(item)


msg="[2022-11-25 11:25:53][Critical][SFP RX][DR DWDM #2 (ALJ0616F091)][Index:15,Slot:N/A,Port:15] SFP Rx Power 118.1uW[Port Speed:1, Threshold:200uW],Linked Devices : N/A"
msg= '[2022-10-01 00:02:29][Critical][SFP RX][N/A (JAF1542CERT)][Index:fc1/1,Slot:1,Port:1] SFP Rx Power 421.7uW [Port Speed:8, Threshold:500uW], Linked Devices : [N/A] N/A(N/A)'
msg= '[2022-10-01 00:02:29][Critical][SFP RX][IDC 통합 SAN#2 (JAF1542CERT)][Index:fc1/1,Slot:1,Port:1] SFP Rx Power 421.7uW [Port Speed:8, Threshold:500uW], Linked Devices : [N/A] N/A(N/A)'
msg = '[2022-11-20 07:47:29][Critical][CRC ERR][IDC 통합 SAN#2 (QV250000196)][Index:137,Slot:1,Port:25] CRC ERR value chaged (91->93) Linked Devices :'
msg = '[2022-11-29 09:00:00][Critical][THROUGHPUT][N/A (BRD0000283)][Index:1,Slot:0,Port:1] Throughput Critical 400 [Port Speed:16G, Threshold:300], Linked Devices : N/A'

msg=msg.split('Linked Devices')[0]
print(msg)

regex = '\[([^]]+)'
text = re.sub(regex,'', msg)
# print(text)
text = text.replace('[', '')
text = text.replace(']', '')
text = text.replace(',', '')
# print(text)


items = re.findall(regex,msg)
# for item in items:
#     print(item)

if len(items) == 6:
    evt_datetime = items[0]
    evt_severity = items[1]
    evt_device = items[2]
    evt_alias  = items[3]
    # evt_alias = evt_alias.split('(')[0]
    evt_portnum  = items[4]
    evt_threshold  = items[5]
elif len(items) == 5:
    evt_datetime = items[0]
    evt_severity = items[1]
    evt_device = items[2]
    evt_alias = items[3]
    # evt_alias = evt_alias.split('(')[0]
    evt_portnum = items[4]

target_msg ="""{ALIAS}의 {MSG}입니다.\n({PORT_NUM})
""".format(ALIAS=evt_alias,PORT_NUM=evt_portnum,MSG=text)
print(target_msg)


