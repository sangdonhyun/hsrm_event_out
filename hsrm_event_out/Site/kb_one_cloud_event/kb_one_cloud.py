import os
import configparser
import fleta_crypto
import json

class event():
    def __init__(self):
        self.fs = fleta_crypto.AESCipher('kes2719!')

    def get_event_json_str(self,event_data):
        json_str_sample="""
        {
        "records"[
        {
            "description": "Monitored 2 long active threads",
            "source": "EZIS",
            "type": "Database Stat", 
            "message_key": "oi_4154a722d03111100740ab547fc7ac57", -- 이벤트 고유 식별자
            "time_of_event": "2022-09-11 02:46:29", -- 이벤트 발생 시각
            "severity": "5", -- 이벤트 심각도
            "node": "192.168.0.1", -- 이벤트와 관련된 노드 리소스예) 디스크 C, CPU-1, 프로세스 또는 서비스명
            "resource": "Instance name"
            “resolution_state”:””
        }
        ]
        }
        """
        json_data = dict()

#         json_str = """{"description": "{EVENT_DESCRIPTION}",
# "source": "HSRM",
# "type": {EVENT_CODE}",
# "message_key": "{EVENT_KEY}",
# "time_of_event": "{EVENT_DATETIME}",
# "severity": "{EVENT_SEVERITY}",
# "node": "{SERIAL}",
# "resource": "{EVENT_TYPE}"
# “resolution_state”:””
# }""".format( EVENT_DESCRIPTION=event_data['description']
#                      , EVENT_TYPE=event_data['event_TYPE']
#                      , EVENT_CODE=event_data['event_CODE']
#                      , EVENT_DATETIME=event_data['event_date']
#                      , EVENT_SEVERITY=event_data['severity']
#                      , SERIAL=event_data['serial']
#                      , EVENT_KEY=event_data['event_uniq_key'])
#         print(json_str)
        json_str = json.dumps(event_data,indent=4)
        return json_str



    def get_event_list_data(self,event_list):
        json_data = dict()
        # json_data["records"] = list()
        list_data = list()
        for event_data in event_list:

            json_str = self.get_event_json_str(event_data)
            json_d= json.loads(json_str)
            list_data.append(json_d)
        json_data["records"] = list_data
        return json_data