# 约定  
permission： support.call_record:list   
link: '/support/call_record'   
type: 2   
时间格式： 时间戳  

## TODO  
是否场外、转接主叫、转接被叫、确认是否必要，重要但是可以先不做，不在列表显示，在详情中    

## 获取通话列表    
url: `/api/support/aliyun_ccc/call_record`     
method: `get`    
params:   
"""
(
    page=1,  
    size=100,  
    agent_names: "", 
    calling_number='07353988****',  
    called_number='1320523****'  
)
"""


resp:   
```json  
{  
"code": 0,  
"message" "",  
"data": {  
        "page": 1,
        "size": 10,
        "total": 1,
        "list": [
           {
        "called_number": "051287810584",
        "ivr_time": 10,
        "contact_type": "_inbound",
        "contact_disposition": "_success",
        "contact_id": "job-52853bef-5f7d-4286-9b68-1181b0a19afc",
        "calling_number": "17831138001",
        "talk_time": 276,
        "release_reason": "200 - _okay",
        "recording_ready": true,
        "skill_group_names": "技术支持",
        "satisfaction_survey_offered": false,
        "established_time": 1686040987223,
        "queue_time": 6,
        "skill_group_ids": "techsupport@hillstone",
        "broker": "",
        "release_initiator": "agent",
        "instance_id": "hillstone",
        "start_time": 1686040987223,
        "ring_time": 6,
        "call_duration": 291,
        "callee_location": "江苏省-苏州",
        "release_time": 1686041277826,
        "satisfaction_survey_channel": "",
        "agent_ids": "cyliu@hillstone",
        "additional_broker": "",
        "satisfaction_description": "",
        "wait_time": 6,
        "caller_location": "河北省-石家庄",
        "dialing_time": 0,
        "agent_names": "刘驰云",
        "recording_duration": 275
      }
    ]
    }
}
```


## 播放下载接口    
播放：https://ccc-v2.aliyun.com/api?action=GetMonoRecording&product=CloudCallCenter&version=2020-07-01&region=cn-shanghai    

本地:  
播放  
URL: '/api/support/aliyun_ccc/call_record/mono_recording'  
Mehtod: GET  
params:  
```
{"contact_id":"job-52853bef-5f7d-4286-9b68-1181b0a19afc"}  
``` 

resp:    
```
{
    "code": 0,
    "message": "",
    "data": {
        "file_url": "https://ccc-v2-online.oss-cn-shanghai.aliyuncs.com/ccc-record-mixed/hillstone/2023/06/job-52853bef-5f7d-4286-9b68-1181b0a19afc.mp3?Expires=1686128021&OSSAccessKeyId=LTAI4GDDtCgcY8HmXTiEhr1q&Signature=cvXTdMiBkckU7v2RSuh5OpzGtmg%3D",
        "file_name": "job-52853bef-5f7d-4286-9b68-1181b0a19afc.mp3"
    }
}
```

## 根据坐席名称获取坐席列表  
URL： '/api/support/aliyun_ccc/agent'  
Mehtod: GET  

params:  
```
{"name_pattern": "", "page": 1, "size":100}  
``` 
resp:    
```
{
    "code": 0,
    "message": "",
    "data": {
        "page": 1,
        "size": 10,
        "total": 1,
        "list": [
        {"login_name":"","email":"","device_id":"IPPhone","primary_account":false,"skill_level_list":[{"skill_level":6,"skill_group_name":"产品咨询","skill_group_id":"salesconsult@hillstone"}],"ram_id":296139145002762862,"display_id":"3386","mobile":"17856001185","role_id":"Agent@hillstone","extension":"80169535","role_name":"Agent","device_state":"ONLINE","user_id":"changjiezhu@hillstone","display_name":"朱常洁","device_ext":"80414537","work_mode":"ON_SITE"}
        ]
    }
}
```


