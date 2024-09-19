
#### 内部员工列表 
url: '/api/internal/hr/staff/list'  
method: get  
params:    

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| keyword | string | 是 | 用户名 |

resp:  
```text
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "3nqn2mdqdnuz2c7",
        "internal_email": "jjlv@Hillstonenet.com",
        "user_name": "吕监军-华中售后服务部-售后工程师"
      }
    ]
  },
  "message": "successful"
}
```