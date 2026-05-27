"""Graylog GELF UDP handler for loguru."""

import json
import os
import platform
import socket
from uuid import uuid4


class GraylogUdpHandler:
    """Loguru handler that sends log messages to Graylog via GELF over UDP.

    Attributes:
        __VERSION__: GELF protocol version.
    """

    __VERSION__ = "1.1"

    def __init__(
        self, host: str = "192.168.1.84", port: int = 12201, log_name: str = "python"
    ) -> None:
        """Initialize the Graylog UDP handler.

        Args:
            host: Graylog server hostname or IP address.
            port: Graylog GELF UDP port (default: 12201).
            log_name: Name identifier for the log source.
        """
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.log_name = log_name
        self.hostname = platform.node()
        self.environment = os.getenv("APP_ENV", "dev")
        self.session_id = str(uuid4())

    def send(self, message) -> None:
        """Send a loguru message to Graylog as a GELF JSON payload.

        Args:
            message: Loguru message object containing the record.
        """
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
            self.sock.sendto(json.dumps(gelf_message).encode(), self.address)
        except Exception as e:
            print(f"Error sending log to Graylog: {e}")

    def __call__(self, message) -> None:
        """Make the handler callable for loguru integration."""
        self.send(message)
