# 辅助平台-终端高亮

```
"p_auxiliary_terminal_highlight": "auxiliary.terminal_highlight:all"

显示路由：
菜单路径：辅助平台->终端高亮
路由：/auxiliary_platform/terminal_highlight

```

### 说明

init_reg为字符串，初始数据来源于https://git.tac.hillstonenet.com/devops/mrpc/-/blob/master/public/data/terminal-highlight.crt ，第三行到最后一行    
terminal_str为字符串， 初始数据来源于https://git.tac.hillstonenet.com/devops/manage-site/-/blob/develop/mock/consts/terminal-highlight.ts ， （注意，这个的init_reg和上面的正则，会有js\\的问题）

## API


### 获取高亮正则和终端命令数据
URL: '/api/auxiliary/terminal_highlight'  
Method: GET  

```json
{
  "code": 0,
  "data": {
    "init_reg": "", //正则
    "terminal_str": "", //命令和结果字符串数据
  },
  "message": "successful"
}
```

### 设置正则/终端命令数据 
URL: '/api/auxiliary/terminal_highlight'  
Method: PUT  
Params：  

| 字段名    | 类型     | 是否必须 | 描述        |
|--------|--------|------|-----------|
| init_reg | string | 否（至少一个）   | 高亮正则 |
| terminal_str     | string   | 否（至少一个）   | 终端命令      |


```json
{
  "code": 0,
  "data": {
  },
  "message": "successful"
}
```