import atexit
import os
import re
import socket

from time import sleep


class LocustMonitor:
    monitoring_host = os.getenv('LOCUST_MONITORING_HOST')
    monitoring_port = int(os.getenv('LOCUST_MONITORING_PORT'))
    sock = None

    def __init__(self):
        self.sock = socket.socket()
        self._connect_socket()
        atexit.register(self.exit_handler)

    def send_result(self, result: str) -> None:
        """ Encode and send the result. """
        plaintext = self.plaintext_namespacing(result)
        encoded = plaintext.encode('utf-8')
        self.sock.send(encoded)

    def exit_handler(self) -> None:
        """ Close the socket on exit. """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    @staticmethod
    def plaintext_namespacing(namespace: str) -> str:
        """ Change namespacing to work with the plaintext protocol. """
        collapsed = re.sub('[.: \]\[]', '', namespace)  # pylint: disable=W1401
        return collapsed

    def plaintext_url(self, namespace:str) -> str:
        finished = re.sub('[/]', '', self.plaintext_namespacing(namespace))
        return finished

    def _connect_socket(self):
        for i in range(0, 5):
            try:
                self.sock.connect(
                    (
                        self.monitoring_host,
                        self.monitoring_port
                    )
                )
                break
            except ConnectionRefusedError:
                sleep(i*i)  # Exponential Backoff For Attempting to Connect
                continue
