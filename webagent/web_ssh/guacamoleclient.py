import traceback

from threading import Thread
from guacamole.client import GuacamoleClient, PROTOCOLS
from webagent.extensions import logger


class Client:
    def __init__(self, websocker):
        self.websocker = websocker
        self.guacamoleclient = None

    def connect(self, protocol, hostname, port, username, password, width, height, dpi, **kwargs):
        try:
            self.guacamoleclient = GuacamoleClient('10.86.248.49', 4822)
            self.guacamoleclient.handshake(
                protocol=protocol,
                hostname=hostname,
                port=port
            )
            Thread(target=self.websocket_to_django).start()

        except Exception as e:
            self.websocker.close(3001)

    def django_to_guacd(self, data):
        try:
            self.guacamoleclient.send(data)
        except Exception as e:
            self.close()

    def websocket_to_django(self):
        try:
            while 1:
                # time.sleep(0.00001)
                data = self.guacamoleclient.receive()
                if not data:
                    print('connect offline...')
                    break
                else:
                    self.websocker.send(data)

        except Exception as e:
            print(e)
        finally:
            self.close()

    def close(self):
        try:
            self.websocker.close()
            self.guacamoleclient.close()
        except Exception:
            logger.error(traceback.format_exc())

    def shell(self, data):
        self.django_to_guacd(data)