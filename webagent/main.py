import os
import logging
import tornado.web
import tornado.ioloop

from tornado.options import options
from webagent.web_ssh import handler
from webagent.web_ssh.settings import get_app_settings,  get_ssl_context, get_server_settings, check_encoding_setting

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_handlers(loop):
    handlers = [
        (r'/webagent/manager/(?P<instance_id>.*?)/(?P<node_id>.*?)/ssh', handler.WebSshHandler, dict(loop=loop)),
        (r'/cloud_lab/cli', handler.WsSockHandler, dict(loop=loop)),
        (r'/webagent/manager/(?P<instance_id>.*?)/(?P<node_id>.*?)/console', handler.WebVncHandler, dict(loop=loop)),
        (r'/cloud_lab/vnc', handler.VncSockHandler, dict(loop=loop)),
        (r'/webagent/manager/(?P<instance_id>.*?)/(?P<node_id>.*?)/gui', handler.WebGuiHandler, dict(loop=loop)),
        (r'/cloud_lab/gui', handler.WebSocketGuiHandler, dict(loop=loop)),
        (r"/webagent/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(base_dir, 'webagent', 'templates')}),
        (r'/webagent/api/instance/(?P<instance_id>.*?)/expire', handler.InstanceExpire, dict(loop=loop)),
    ]
    return handlers


def make_app(handlers, settings):
    settings.update(default_handler_class=handler.NotFoundHandler)
    return tornado.web.Application(handlers, **settings)


def app_listen(app, port, address, server_settings):
    app.listen(port, address, **server_settings)
    if not server_settings.get('ssl_options'):
        server_type = 'http'
    else:
        server_type = 'https'
        handler.redirecting = True if options.redirect else False
    logging.info('Listening on {}:{} ({})'.format(address, port, server_type))


def agent_app():
    check_encoding_setting(options.encoding)
    loop = tornado.ioloop.IOLoop.current()
    app = make_app(make_handlers(loop), get_app_settings(options))
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    app_listen(app, options.port, options.address, server_settings)
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app_listen(app, options.sslport, options.ssladdress, server_settings)
    loop.start()
