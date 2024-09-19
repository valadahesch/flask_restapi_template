import tornado.websocket
import os
import socket
import traceback

from webagent.extensions import logger
from tornado.ioloop import IOLoop
from tornado.iostream import _ERRNO_CONNRESET
from tornado.util import errno_from_exception
from guacamole.client import GuacamoleClient


BUF_SIZE = 32 * 1024
clients = {}  # {ip: {id: worker}}
vnc_clients = {}


def clear_worker(worker, clients):
    ip = worker.src_addr[0]
    workers = clients.get(ip)
    assert worker.id in workers
    workers.pop(worker.id)

    if not workers:
        clients.pop(ip)
        if not clients:
            clients.clear()


def recycle_worker(worker):
    if worker.handler:
        return
    worker.close(reason='worker recycled')
    logger.warning(f'worker: {worker.id} recycle exit')


class Worker(object):
    src_addr = ""

    def __init__(self, loop, ssh, chan, dst_addr):
        self.loop = loop
        self.ssh = ssh
        self.chan = chan
        self.dst_addr = dst_addr
        self.fd = chan.fileno()
        self.id = str(id(self))
        self.data_to_dst = []
        self.handler = None
        self.mode = IOLoop.READ
        self.closed = False
        if not os.path.isdir("log"):
            os.mkdir("log")
        self.f = open("log/{}.log".format(self.id), "wb")

    def __call__(self, fd, events):
        if events & IOLoop.READ:
            self.on_read()
        if events & IOLoop.WRITE:
            self.on_write()
        if events & IOLoop.ERROR:
            self.close(reason='error event occurred')

    def set_handler(self, handler):
        if not self.handler:
            self.handler = handler

    def update_handler(self, mode):
        if self.mode != mode:
            self.loop.update_handler(self.fd, mode)
            self.mode = mode
        if mode == IOLoop.WRITE:
            self.loop.call_later(0.1, self, self.fd, IOLoop.WRITE)

    def on_read(self):
        logger.debug('worker {} on read'.format(self.id))
        try:
            data = self.chan.recv(BUF_SIZE)
        except (OSError, IOError) as e:
            logger.error(e)
            if self.chan.closed or errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close(reason='chan error on reading')
        else:
            logger.debug('{!r} from {}:{}'.format(data, *self.dst_addr))
            if not data:
                self.close(reason='chan closed')
                return

            cmd = processReadLine(bytes.decode(data))
            self.f.write(str.encode(cmd))

            logger.debug('{!r} to {}:{}'.format(cmd, *self.handler.src_addr))
            try:
                self.handler.write_message(data)
            except tornado.websocket.WebSocketClosedError:
                self.close(reason='websocket closed')

    def on_write(self):
        logger.debug('worker {} on write'.format(self.id))
        if not self.data_to_dst:
            return

        data = ''.join(self.data_to_dst)
        logger.debug('{!r} to {}:{}'.format(data, *self.dst_addr))

        try:
            sent = self.chan.send(data)
        except (OSError, IOError) as e:
            logger.error(e)
            if self.chan.closed or errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close(reason='chan error on writing')
            else:
                self.update_handler(IOLoop.WRITE)
        else:
            self.data_to_dst = []
            data = data[sent:]
            if data:
                self.data_to_dst.append(data)
                self.update_handler(IOLoop.WRITE)
            else:
                self.update_handler(IOLoop.READ)

    def close(self, reason=None):
        if self.closed:
            return
        self.closed = True

        logger.info(
            'Closing worker {} with reason: {}'.format(self.id, reason)
        )
        if self.handler:
            self.loop.remove_handler(self.fd)
            self.handler.close(reason=reason)
        self.chan.close()
        self.ssh.close()
        logger.info('Connection to {}:{} lost'.format(*self.dst_addr))

        clear_worker(self, clients)
        self.f.close()
        logger.debug(clients)


def processReadLine(line_p):
    '''
    remove non-printable characters from line <line_p>
    return a printable string.
    '''

    line, i, imax = '', 0, len(line_p)
    while i < imax:
        ac = ord(line_p[i])
        if (32<=ac<127) or ac in (9,10):
            line += line_p[i]
        elif ac == 27:
            i += 1
            while i<imax and line_p[i].lower() not in 'abcdhsujkm':
                i += 1
        elif (ac==13 and line and line[-1] == ' '): # backspace or EOL spacing
            if line:
                line = line[:-1]
        i += 1

    return line


class ProxyWorker(object):
    src_addr = ""

    def __init__(self, loop, vnc_host, vnc_port):
        self.vnc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vnc_socket.connect((vnc_host, vnc_port))
        self.vnc_socket.settimeout(60)
        self.handler = None
        self.fd = self.vnc_socket.fileno()
        self.id = str(id(self))
        self.loop = loop
        self.closed = False

    def set_handler(self, handler):
        self.handler = handler

    def vnc_to_handler(self):
        while True:
            try:
                data = self.vnc_socket.recv(10240)
                if not data:
                    logger.info(f"vnc_to_handler data is None")
                    break
                try:
                    self.handler.write_message(data, binary=True)
                except AssertionError as e:
                    print(f'vnc_to_handler AssertionError: {repr(e)}, Data: {data}')
                    continue

            except Exception as e:
                logger.info(f"vnc_to_handler exception: {str(e)}")
                break

        if not self.closed:
            if self.handler:
                self.loop.remove_handler(self.fd)
                self.handler.close(reason="socket close")
            self.closed = True
            logger.info('socket close')

    def handler_to_vnc(self, data):
        try:
            if data and isinstance(data, bytes):
                self.vnc_socket.send(data)
            elif data and isinstance(data, str):
                self.vnc_socket.send(data.encode())
        except Exception as e:
            self.handler.close(reason=str(e))

    def close(self, reason):
        # Close the underlying socket
        try:
            self.vnc_socket.close()
        except Exception as e:
            print(f"socket close: {str(e)}")

        if self.handler and not self.closed:
            self.loop.remove_handler(self.fd)
            self.handler.close(reason=reason)

        clear_worker(self, vnc_clients)
        self.closed = True


class GuacamoleProxy:
    src_addr = ""

    def __init__(self, loop, protocol, hostname, port):
        self.client = GuacamoleClient('10.86.248.49', 4822)
        self.client.handshake(
            protocol=protocol,
            hostname=hostname,
            port=port
        )
        self.handler = None
        self.id = str(id(self))
        self.fd = self.client.client.fileno()
        self.loop = loop
        self.closed = False

    def set_handler(self, handler):
        self.handler = handler

    def on_read_guacd(self):
        try:
            while True:
                try:
                    data = self.client.receive()
                    if not data:
                        break
                except Exception as e:
                    print(f'on_read_guacd client Exception: {repr(e)}')
                    break
                try:
                    self.handler.write_message(data)
                except AssertionError as e:
                    print(f'on_read_guacd AssertionError: {repr(e)}, Data: {data}')
                    continue
                except Exception as e:
                    traceback.print_exc()
                    print(f'on_read_guacd Exception: {repr(e)}, Data: {data}')
                    break

        except Exception as e:
            print(f'on_read_guacd Exception: {str(e)}')

        if not self.closed:
            if self.handler:
                self.handler.close(reason="socket close")
            self.closed = True
            logger.info('socket close')

    def on_write_guacd(self, data):
        try:
            self.client.send(data)
        except Exception as e:
            self.close(f"on_write exception: {str(e)}")

    def close(self, reason):
        # Close the underlying socket
        try:
            print(f'guacamole close')
            self.client.close()
        except Exception as e:
            print(f"guacamole close exception: {str(e)}")

        if self.handler and not self.closed:
            self.handler.close(reason=reason)

        clear_worker(self, vnc_clients)
        self.closed = True