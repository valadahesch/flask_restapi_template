import asyncio
import os
import json
import socket
import traceback
import weakref
import paramiko
import tornado.web
import tornado.gen
import tornado.websocket

from webagent.extensions import redis_client, logger
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.process import cpu_count
from webagent.web_ssh.utils import is_valid_port, to_str, to_int, to_ip_address, is_ip_hostname, \
    is_same_primary_domain, is_valid_encoding
from webagent.web_ssh.worker import Worker, recycle_worker, clients, ProxyWorker, vnc_clients, GuacamoleProxy

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

DEFAULT_PORT = 22

swallow_http_errors = True
redirecting = None


class InvalidValueError(Exception):
    pass


class SSHClient(paramiko.SSHClient):

    def handler(self, prompt_list):
        answers = []
        for prompt_, _ in prompt_list:
            prompt = prompt_.strip().lower()
            if prompt.startswith('password'):
                answers.append(self.password)
            elif prompt.startswith('verification'):
                answers.append(self.totp)
            else:
                raise ValueError('Unknown prompt: {}'.format(prompt_))
        return answers

    def auth_interactive(self, username, handler):
        if not self.totp:
            raise ValueError('Need a verification code for 2fa.')
        self._transport.auth_interactive(username, handler)

    def _auth(self, username, password, pkey, *args):
        self.password = password
        saved_exception = None
        two_factor = False
        two_factor_types = {'keyboard-interactive', 'password'}

        if pkey is not None:
            logger.info('Trying publickey authentication')
            try:
                allowed_types = set(
                    self._transport.auth_publickey(username, pkey)
                )
                two_factor = allowed_types & two_factor_types
                if not two_factor:
                    return
            except paramiko.SSHException as e:
                saved_exception = e

        if two_factor:
            logger.info('Trying publickey 2fa')
            return self.auth_interactive(username, self.handler)

        if password is not None:
            logger.info('Trying password authentication')
            try:
                self._transport.auth_password(username, password)
                return
            except paramiko.SSHException as e:
                saved_exception = e
                allowed_types = set(getattr(e, 'allowed_types', []))
                two_factor = allowed_types & two_factor_types

        if two_factor:
            logger.info('Trying password 2fa')
            return self.auth_interactive(username, self.handler)

        assert saved_exception is not None
        raise saved_exception


class MixinHandler(object):
    custom_headers = {
        'Server': 'TornadoServer'
    }

    html = ('<html><head><title>{code} {reason}</title></head><body>{code} '
            '{reason}</body></html>')

    def initialize(self, loop=None):
        self.check_request()
        self.loop = loop
        self.origin_policy = self.settings.get('origin_policy')

    def check_request(self):
        context = self.request.connection.context
        result = self.is_forbidden(context, self.request.host_name)
        self._transforms = []
        if result:
            self.set_status(403)
            self.finish(
                self.html.format(code=self._status_code, reason=self._reason)
            )
        elif result is False:
            to_url = self.get_redirect_url(
                self.request.host_name, options.sslport, self.request.uri
            )
            self.redirect(to_url, permanent=True)
        else:
            self.context = context

    def check_origin(self, origin):
        if self.origin_policy == '*':
            return True

        parsed_origin = urlparse(origin)
        netloc = parsed_origin.netloc.lower()
        logger.debug('netloc: {}'.format(netloc))

        host = self.request.headers.get('Host')
        logger.debug('host: {}'.format(host))

        if netloc == host:
            return True

        if self.origin_policy == 'same':
            return True
        elif self.origin_policy == 'primary':
            return is_same_primary_domain(netloc.rsplit(':', 1)[0],
                                          host.rsplit(':', 1)[0])
        else:
            return origin in self.origin_policy

    def is_forbidden(self, context, hostname):
        ip = context.address[0]
        lst = context.trusted_downstream
        ip_address = None

        if lst and ip not in lst:
            logger.warning(
                'IP {!r} not found in trusted downstream {!r}'.format(ip, lst)
            )
            return True

        if context._orig_protocol == 'http':
            if redirecting and not is_ip_hostname(hostname):
                ip_address = to_ip_address(ip)
                if not ip_address.is_private:
                    # redirecting
                    return False

            if options.fbidhttp:
                if ip_address is None:
                    ip_address = to_ip_address(ip)
                if not ip_address.is_private:
                    logger.warning('Public plain http request is forbidden.')
                    return True

    def get_redirect_url(self, hostname, port, uri):
        port = '' if port == 443 else ':%s' % port
        return 'https://{}{}{}'.format(hostname, port, uri)

    def set_default_headers(self):
        for header in self.custom_headers.items():
            self.set_header(*header)

    def get_value(self, name):
        value = self.get_argument(name)
        if not value:
            raise InvalidValueError('Missing value {}'.format(name))
        return value

    def get_context_addr(self):
        return self.context.address[:2]

    def get_client_addr(self):
        if options.xheaders:
            return self.get_real_client_addr() or self.get_context_addr()
        else:
            return self.get_context_addr()

    def get_real_client_addr(self):
        ip = self.request.remote_ip
        if ip == "::1":
            ip = '127.0.0.1'
        port = None
        if ip == self.request.headers.get('X-Real-Ip'):
            port = self.request.headers.get('X-Real-Port')
        elif ip in self.request.headers.get('X-Forwarded-For', ''):
            port = self.request.headers.get('X-Forwarded-Port')

        port = to_int(port)
        if port is None or not is_valid_port(port):
            port = 65535

        return (ip, port)


class NotFoundHandler(MixinHandler, tornado.web.ErrorHandler):

    def initialize(self):
        super(NotFoundHandler, self).initialize()

    def prepare(self):
        raise tornado.web.HTTPError(404)


class InstanceExpire(MixinHandler, tornado.web.RequestHandler):
    result = dict(code=0, data={}, message='')

    def initialize(self, loop):
        super(InstanceExpire, self).initialize(loop)

    def get(self, instance_id):
        expire_key = f"ttl:cloudlab:{instance_id}:delete"
        expire = redis_client.ttl(expire_key)
        data = {"id": instance_id, "name": "", "expire": expire}
        self.result.update(data=data)
        self.write(self.result)


class WebSshHandler(MixinHandler, tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)
    result = dict(code=-1, data={}, message='')

    def initialize(self, loop):
        super(WebSshHandler, self).initialize(loop)
        self.ws_url = 'wss://linkapitest.tac.hillstonenet.com'
        env = os.environ.get('APP_ENV', 'local')
        if env == 'local':
            self.ws_url = 'ws://127.0.0.1:8081'
        if env == 'prod':
            self.ws_url = 'wss://linkapi.hillstonenet.com'

    def parse_encoding(self, data):
        try:
            encoding = to_str(data.strip(), 'ascii')
        except UnicodeDecodeError:
            return

        if is_valid_encoding(encoding):
            return encoding

    def get_default_encoding(self, ssh):
        commands = [
            '$SHELL -ilc "locale charmap"',
            '$SHELL -ic "locale charmap"'
        ]

        for command in commands:
            try:
                _, stdout, _ = ssh.exec_command(command, get_pty=True)
            except paramiko.SSHException as exc:
                logger.info(str(exc))
            else:
                data = stdout.read()
                logger.debug('{!r} => {!r}'.format(command, data))
                result = self.parse_encoding(data)
                if result:
                    return result

        logger.warning('Could not detect the default encoding.')
        return 'utf-8'

    def get_login(self, mode, instance_id, node_id):
        try:
            key = f"techadmin:cloudlab:{instance_id}:{node_id}:{mode}"
            value = redis_client.get(key)
            if value:
                value = json.loads(value)

        except:
            value = {
                'host': '10.88.16.75', 'port': 2222, 'username': 'hillstone',
                'password': 'hillstone123'
            }

        return value['host'], str(value['port']), value['username'], value['password']

    def ssh_connect(self, host, port, username, password):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logger.info(f'Connecting to {host}:{port}')

        try:
            ssh.connect(hostname=host, port=port, username=username, password=password, timeout=options.timeout)
        except socket.error:
            raise ValueError(f'Unable to connect to {host}:{port}')
        except paramiko.BadAuthenticationType:
            raise ValueError('Bad authentication type.')
        except paramiko.AuthenticationException:
            raise ValueError('Authentication failed.')
        except paramiko.BadHostKeyException:
            raise ValueError('Bad host key.')

        term = self.get_argument('term', u'') or u'xterm'
        chan = ssh.invoke_shell(term=term)
        chan.setblocking(0)
        worker = Worker(self.loop, ssh, chan, (host, port))
        worker.encoding = options.encoding if options.encoding else self.get_default_encoding(ssh)
        return worker

    @tornado.gen.coroutine
    def get(self, instance_id, node_id):
        ip, port = self.get_client_addr()
        workers = clients.get(ip, {})
        if workers and len(workers) >= options.maxconn:
            self.result.update(message="Too many live connections.")
            self.write(self.result)
            return

        node_key = f"techadmin:cloudlab:{instance_id}:{node_id}:ssh"
        value = redis_client.get(node_key)
        if not value:
            self.result.update(message="Failed to obtain node information")
            self.write(self.result)
            return

        value = json.loads(value)
        if value.get("token"):
            if value.pop("token") != self.get_argument("token"):
                self.result.update(message="Authentication failed")
                self.write(self.result)
                return
        elif value.get("user_id"):
            if value.get("user_id") != self.get_cookie("user_id"):
                self.result.update(message="Permission denied")
                self.write(self.result)
                return

        login_args = (value["host"], value["port"], value["login_user"], value["login_password"])
        future = self.executor.submit(self.ssh_connect, *login_args)

        try:
            worker = yield future
        except (ValueError, paramiko.SSHException) as exc:
            logger.error(traceback.format_exc())
            self.result.update(status=str(exc))
            self.write(self.result)
            return self.request
        else:
            if not workers:
                clients[ip] = workers
            worker.src_addr = (ip, port)
            workers[worker.id] = worker
            self.loop.call_later(options.delay, recycle_worker, worker)
            self.result.update(id=worker.id, encoding=worker.encoding)

        node_ttl = redis_client.ttl(value["instance_redis_key"])
        redis_client.setex(node_key, node_ttl, json.dumps(value))
        self.set_cookie("user_id", value["user_id"])
        self.render(
            'cli.html', ws_id=worker.id, ws_url=self.ws_url, node_name=value["node_name"],
            instance_id=instance_id, instance_name=value["instance_name"],
            user_name=value["user_name"], node_id=node_id, login_name=value.get("login_name"),
            username=value.get("login_user"), password=value.get("login_password")
        )


class WsSockHandler(MixinHandler, tornado.websocket.WebSocketHandler):
    worker_ref = None
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)

    def initialize(self, loop):
        super(WsSockHandler, self).initialize(loop)

    def open(self):
        self.src_addr = self.get_client_addr()
        logger.info('Connected from {}:{}'.format(*self.src_addr))

        workers = clients.get(self.src_addr[0])
        if not workers:
            self.close(reason='Websocket authentication failed.')
            return

        try:
            worker_id = self.get_value('ws_id')
        except (tornado.web.MissingArgumentError, InvalidValueError) as exc:
            self.close(reason=str(exc))
        else:
            worker = workers.get(worker_id)
            if worker:
                workers[worker_id] = None
                self.set_nodelay(True)
                worker.set_handler(self)
                self.worker_ref = weakref.ref(worker)
                self.loop.add_handler(worker.fd, worker, IOLoop.READ)
            else:
                self.close(reason='Websocket authentication failed.')

    def on_message(self, message):
        # logger.debug('{!r} from {}:{}'.format(message, *self.src_addr))
        worker = self.worker_ref()
        if message:
            worker.data_to_dst.append(message)
            worker.on_write()

    def on_close(self):
        if not self.close_reason:
            self.close_reason = 'client disconnected'

        worker = self.worker_ref() if self.worker_ref else None
        if worker:
            worker.close(reason=self.close_reason)
            workers = clients.get(worker.node_id)
            if worker.id in workers.keys():
                workers.pop(worker.id)
        logger.debug('WebSocket closed')


class WebVncHandler(MixinHandler, tornado.web.RequestHandler):
    result = dict(code=-1, data={}, message='')
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)

    def initialize(self, loop):
        super(WebVncHandler, self).initialize(loop)
        self.ws_url = 'wss://linkapitest.tac.hillstonenet.com'
        env = os.environ.get('APP_ENV', 'local')
        if env == 'local':
            self.ws_url = 'ws://127.0.0.1:8081'
        if env == 'prod':
            self.ws_url = 'wss://linkapi.hillstonenet.com'

    def vnc_server(self, host, port):
        worker = ProxyWorker(self.loop, host, port)
        return worker

    @tornado.gen.coroutine
    def get(self, instance_id, node_id):
        ip, port = self.get_client_addr()
        workers = vnc_clients.get(ip, {})
        if workers and len(workers) >= options.maxconn:
            self.result.update(message="Too many live connections.")
            self.write(self.result)
            return

        node_key = f"techadmin:cloudlab:{instance_id}:{node_id}:console"
        value = redis_client.get(node_key)
        if not value:
            self.result.update(message="Failed to obtain node information")
            self.write(self.result)
            return

        value = json.loads(value)
        if value.get("token"):
            if value.pop("token") != self.get_argument("token"):
                self.result.update(message="Authentication failed")
                self.write(self.result)
                return
        elif value.get("user_id"):
            if value.get("user_id") != self.get_cookie("user_id"):
                self.result.update(message="Permission denied")
                self.write(self.result)
                return

        future = self.executor.submit(self.vnc_server, *(value["host"], int(value["port"])))

        try:
            worker = yield future
        except (ValueError, paramiko.SSHException) as exc:
            logger.error(traceback.format_exc())
            self.result.update(status=str(exc))
            self.write(self.result)
            return self.request
        else:
            if not workers:
                vnc_clients[ip] = workers
            worker.src_addr = (ip, port)
            workers[worker.id] = worker
            self.loop.call_later(10, recycle_worker, worker)
            logger.info(f'worker: {worker.id} create')

        self.render(
            'vnc.html',
            ws_id=worker.id, ws_url=self.ws_url, node_name=value["node_name"],
            instance_id=instance_id, instance_name=value["instance_name"],
            user_name=value["user_name"], node_id=node_id, login_name=value.get("login_name"),
            username=value.get("login_user"), password=value.get("login_password")
        )


class VncSockHandler(MixinHandler, tornado.websocket.WebSocketHandler):
    worker_ref = None
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)

    def initialize(self, loop):
        self.loop = loop
        super(VncSockHandler, self).initialize(loop)

    def open(self):
        self.src_addr = self.get_client_addr()
        logger.info('Connected from {}:{}'.format(*self.src_addr))
        workers = vnc_clients.get(self.src_addr[0])
        if not workers:
            self.close(reason='Websocket authentication failed.')
            return

        try:
            worker_id = self.get_value('ws_id')
        except (tornado.web.MissingArgumentError, InvalidValueError) as exc:
            self.close(reason=str(exc))
        else:
            self.worker = workers.get(worker_id)
            if self.worker:
                workers[worker_id] = None
                self.worker.set_handler(self)
                self.worker_ref = weakref.ref(self.worker)
                self.loop.add_handler(self.worker.fd, self.worker, IOLoop.READ)
                logger.info(f'queue_size: {self.executor._work_queue.qsize()}')
                self.executor.submit(self.forwarding, f'worker: {self.worker.id} forwarding start')
                logger.info(f'worker: {self.worker.id} webSocket start')
            else:
                self.close(reason='Websocket authentication failed.')

    def on_message(self, message):
        # 接收来自WebSocket客户端的消息并将其发送到VNC服务器
        # logger.debug('{!r} from {}:{}'.format(message, *self.src_addr))
        self.worker.handler_to_vnc(message)

    def on_close(self):
        self.worker.close("WebSocket closed")
        logger.debug(f'worker: {self.worker.id} webSocket end')

    def forwarding(self, message):
        # 将从VNC服务器接收到的数据发送到WebSocket客户端
        logger.info(message)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.worker.vnc_to_handler()
        loop.close()
        logger.info(f'worker: {self.worker.id} forwarding end')


class WebGuiHandler(MixinHandler, tornado.web.RequestHandler):
    result = dict(code=-1, data={}, message='')
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)

    def initialize(self, loop):
        super(WebGuiHandler, self).initialize(loop)
        self.ws_url = 'wss://linkapitest.tac.hillstonenet.com'
        env = os.environ.get('APP_ENV', 'local')
        if env == 'local':
            self.ws_url = 'ws://127.0.0.1:8081'
        if env == 'prod':
            self.ws_url = 'wss://linkapi.hillstonenet.com'

    def guacd_server(self, protocol, host, port):
        worker = GuacamoleProxy(self.loop, protocol, host, port)
        return worker

    @tornado.gen.coroutine
    def get(self, instance_id, node_id):
        ip, port = self.get_client_addr()
        workers = vnc_clients.get(ip, {})
        if workers and len(workers) >= options.maxconn:
            self.result.update(message="Too many live connections.")
            self.write(self.result)
            return

        node_key = f"techadmin:cloudlab:{instance_id}:{node_id}:console"
        value = redis_client.get(node_key)
        if not value:
            self.result.update(message="Failed to obtain node information")
            self.write(self.result)
            return

        value = json.loads(value)
        if value.get("token"):
            if value.pop("token") != self.get_argument("token"):
                self.result.update(message="Authentication failed")
                self.write(self.result)
                return
        elif value.get("user_id"):
            if value.get("user_id") != self.get_cookie("user_id"):
                self.result.update(message="Permission denied")
                self.write(self.result)
                return

        future = self.executor.submit(self.guacd_server, *('vnc', value["host"], int(value["port"])))

        try:
            worker = yield future
        except (ValueError, paramiko.SSHException) as exc:
            logger.error(traceback.format_exc())
            self.result.update(status=str(exc))
            self.write(self.result)
            return self.request
        else:
            if not workers:
                vnc_clients[ip] = workers
            worker.src_addr = (ip, port)
            workers[worker.id] = worker
            self.loop.call_later(60, recycle_worker, worker)
            logger.info(f'worker: {worker.id} create')

        # self.result.update(data=f"ws_id={worker.id}&node_id={node_id}")
        # self.write(self.result)
        self.render(
            'gui.html',
            ws_id=worker.id, ws_url=self.ws_url, node_name=value["node_name"],
            instance_id=instance_id, instance_name=value["instance_name"],
            user_name=value["user_name"], node_id=node_id, login_name=value.get("login_name"),
            username=value.get("login_user"), password=value.get("login_password")
        )


class WebSocketGuiHandler(MixinHandler, tornado.websocket.WebSocketHandler):
    worker_ref = None
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)

    def initialize(self, loop):
        self.loop = loop
        super(WebSocketGuiHandler, self).initialize(loop)

    def open(self):
        self.src_addr = self.get_client_addr()
        logger.info('Connected from {}:{}'.format(*self.src_addr))
        workers = vnc_clients.get(self.src_addr[0])
        if not workers:
            self.close(reason='Websocket authentication failed.')
            return

        try:
            worker_id = self.get_value('ws_id')
        except (tornado.web.MissingArgumentError, InvalidValueError) as exc:
            self.close(reason=str(exc))
        else:
            self.worker = workers.get(worker_id)
            if self.worker:
                workers[worker_id] = None
                self.worker.set_handler(self)
                self.worker_ref = weakref.ref(self.worker)
                self.loop.add_handler(self.worker.fd, self.worker, IOLoop.READ)
                logger.info(f'queue_size: {self.executor._work_queue.qsize()}')
                self.executor.submit(self.forwarding, f'worker: {self.worker.id} forwarding start')
                logger.info(f'worker: {self.worker.id} webSocket start')
            else:
                self.close(reason='Websocket authentication failed.')

    def on_message(self, message):
        # 接收来自WebSocket客户端的消息并将其发送到VNC服务器
        logger.debug('{!r} from {}:{}'.format(message, *self.src_addr))
        self.worker.on_write_guacd(message)

    def on_close(self):
        self.worker.close("WebSocket closed")
        logger.debug(f'worker: {self.worker.id} webSocket end')

    def forwarding(self, message):
        # 将从VNC服务器接收到的数据发送到WebSocket客户端
        logger.info(message)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.worker.on_read_guacd()
        loop.close()
        logger.info(f'worker: {self.worker.id} forwarding end')

    def select_subprotocol(self, subprotocols):
        # 选择 Guacamole 子协议
        return "guacamole"
