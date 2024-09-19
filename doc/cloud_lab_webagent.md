
#### webagent页面的接口

1.获取实例倒计时接口，轻量化的，8秒一次轮询
```shell
- method: GET
- url : /webagent/api/instance/:instance_id/expire
```

```json
resp:
{
    "code": 0,
    "message": "",
    "data": {
        "id": "",
        "name": "",
        "expire": 300
    }
}
```

