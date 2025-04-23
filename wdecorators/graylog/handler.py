import os
import platform
import socket
import json
from uuid import uuid4


class GraylogUdpHandler:

    __VERSION__ = "1.1"

    def __init__(self, host="192.168.1.84", port=12201, log_name: str = "python"):
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.log_name = log_name
        self.hostname = platform.node()
        self.environment = os.getenv("APP_ENV", "dev")
        self.session_id = str(
            uuid4()
        )  # identificador de sesión/log útil para correlación

    def send(self, message):
        record = message.record

        gelf_message = {
            "version": self.__VERSION__,
            "host": self.hostname,
            "short_message": record["message"],
            "full_message": record.get("exception", ""),
            "timestamp": record["time"].timestamp(),
            "level": record["level"].no,
            "_logger": self.log_name,
            "_module": record["module"],
            "_function": record["function"],
            "_line": record["line"],
            "_file": record["file"].name,
            "_environment": self.environment,
            "_session_id": self.session_id,
            "_process": record["process"].id,
            "_thread": record["thread"].id,
            "_thread_name": record["thread"].name,
            "_user_id": record["extra"].get("user_id", "unknown"),
            "_task": record["extra"].get("task", "unknown"),
        }

        try:
            # self.sock.sendto(json.dumps(gelf_message).encode("utf-8"), self.address)
            self.sock.sendto(json.dumps(gelf_message).encode(), self.address)
        except Exception as e:
            print(f"Error sending log to Graylog: {e}")

    def __call__(self, message):
        self.send(message)
