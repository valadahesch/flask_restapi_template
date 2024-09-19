from tornado import websocket, web, ioloop
import os
import json

cl = []
expire = 308

class WebagentApiHandler(web.RequestHandler):
    def get(self):
        global expire
        expire -= 8
        r = json.dumps({
            'code': 0,
            'message': '',
            'data': {
                "id": '1',
                 "name": "实例名称",
                "expire": expire
            }
        })
        self.write(r)
        

class IndexHandler(web.RequestHandler):
    def get(self):
        # 设置cookie, ws_id, 用户名，用户id
        
        self.render("../templates/cli.html", 
                    ws_id="ws_id:111111",
                    node_id="aa",
                    node_name="节点a",
                    instance_id="1",
                    instance_name="实例名称b",
                    login_name="管理名称",
                    user_name="张三",
                    ws_url="ws://localhost:8888",
                    username="张三",
					password="password"
        )

class ConsoleHandler(web.RequestHandler):
    def get(self):
        self.render("../templates/vnc.html", 
                    ws_id="ws_id:111111",
                    node_id="aa",
                    node_name="节点a",
                    instance_id="1",
                    instance_name="实例名称b",
                    login_name="管理名称",
                    user_name="张三",
                    ws_url="ws://localhost:8888",
                    username="张三",
					password="password"
        )

class GuiHandler(web.RequestHandler):
    def get(self):
        self.render("../templates/gui.html", 
                    ws_id="ws_id:111111",
                    node_id="aa",
                    node_name="节点a",
                    instance_id="1",
                    instance_name="实例名称b",
                    login_name="管理名称",
                    user_name="张三",
                    ws_url="ws://localhost:8888",
                    username="张三",
					password="password"
        )

class CliSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            print("ws_id:", self.get_query_argument("ws_id"))
            cl.append(self)

    def on_message(self, message):
        print("消息", message)
        data  = '''
show version
Hillstone Networks StoneOS software, Version 5.5
Copyright (c) 2009-2023 by Hillstone Networks

Product name: SG-6000-AX1000S S/N: 261030KSD0149767 Assembly number: A011
Boot file is SG6000-AX-5.5R8-3.5-v6
Storage UUID is 6a35842a-79b2-4ab9-b68d-03015e19cc03
Update magic: 021337d30100f3
Built by buildmaster8 2023/09/08 14:13:04

Uptime is 7 days 12 hours 23 minutes 54 seconds
System language is "en"

VRouter feature: enabled

APP feature: enabled
APP magic: 494a528cade19c4ee0a70485ce58f79872e5

geolocation-IP-signature engine version: 0
'''

        self.write_message(data)

    def on_close(self):
        if self in cl:
            cl.remove(self)


app = web.Application([
    (r'/', IndexHandler),
    (r'/console', ConsoleHandler),
    (r'/cloud_lab/cli', CliSocketHandler),
    (r'/cloud_lab/gui', GuiHandler),
    (r'/webagent/api/instance/.*/expire', WebagentApiHandler),
    (r"/webagent/static/(.*)", web.StaticFileHandler, {"path": os.path.abspath(os.path.join(os.getcwd(), "webagent/templates"))}),
])


if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()