"""Tests for GraylogUdpHandler."""
import json
import platform
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from wdecorators.graylog.handler import GraylogUdpHandler


def _make_record(**overrides):
    base = {
        "message": "test msg",
        "exception": None,
        "time": SimpleNamespace(timestamp=lambda: 1234567890.0),
        "level": SimpleNamespace(no=6),
        "module": "test_module",
        "function": "test_func",
        "line": 42,
        "file": SimpleNamespace(name="test_file.py"),
        "process": SimpleNamespace(id=1001),
        "thread": SimpleNamespace(id=2001, name="MainThread"),
        "extra": {},
    }
    base.update(overrides)
    return base


def _make_message(record):
    msg = MagicMock()
    msg.record = record
    return msg


def test_init_sets_attributes():
    handler = GraylogUdpHandler(host="10.0.0.1", port=12345, log_name="test-app")
    assert handler.address == ("10.0.0.1", 12345)
    assert handler.log_name == "test-app"
    assert handler.hostname == platform.node()
    assert handler.environment == "dev"
    assert handler.session_id is not None


@patch("wdecorators.graylog.handler.socket.socket")
def test_send_builds_gelf_message(mock_socket_cls):
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock
    handler = GraylogUdpHandler(host="1.2.3.4", port=12201)

    handler.send(_make_message(_make_record()))

    sent_data = mock_sock.sendto.call_args[0][0]
    payload = json.loads(sent_data)
    assert payload["version"] == "1.1"
    assert payload["short_message"] == "test msg"
    assert payload["full_message"] is None
    assert payload["_user_id"] == "unknown"
    assert payload["_task"] == "unknown"
    assert payload["_module"] == "test_module"
    assert payload["_function"] == "test_func"
    assert payload["_line"] == 42
    assert payload["_file"] == "test_file.py"
    assert mock_sock.sendto.call_args[0][1] == ("1.2.3.4", 12201)


@patch("wdecorators.graylog.handler.socket.socket")
def test_send_with_extra_fields(mock_socket_cls):
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock
    handler = GraylogUdpHandler()

    record = _make_record(extra={"user_id": "alice", "task": "onboarding"})
    handler.send(_make_message(record))

    payload = json.loads(mock_sock.sendto.call_args[0][0])
    assert payload["_user_id"] == "alice"
    assert payload["_task"] == "onboarding"


@patch("wdecorators.graylog.handler.socket.socket")
def test_send_with_exception(mock_socket_cls):
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock
    handler = GraylogUdpHandler()

    exc_info = "Traceback ... ValueError: bad"
    record = _make_record(exception=exc_info, level=SimpleNamespace(no=4))
    handler.send(_make_message(record))

    payload = json.loads(mock_sock.sendto.call_args[0][0])
    assert payload["full_message"] == exc_info
    assert payload["level"] == 4


@patch("wdecorators.graylog.handler.socket.socket")
def test_send_socket_error_caught(mock_socket_cls):
    mock_sock = MagicMock()
    mock_sock.sendto.side_effect = OSError("network unreachable")
    mock_socket_cls.return_value = mock_sock
    handler = GraylogUdpHandler()

    handler.send(_make_message(_make_record()))
    mock_sock.sendto.assert_called_once()


@patch("wdecorators.graylog.handler.socket.socket")
def test_call_delegates_to_send(mock_socket_cls):
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock
    handler = GraylogUdpHandler()

    handler(_make_message(_make_record(message="via call")))

    payload = json.loads(mock_sock.sendto.call_args[0][0])
    assert payload["short_message"] == "via call"


@patch("wdecorators.graylog.handler.socket.socket")
def test_send_socket_timeout_caught(mock_socket_cls):
    mock_sock = MagicMock()
    mock_sock.sendto.side_effect = TimeoutError("timed out")
    mock_socket_cls.return_value = mock_sock
    handler = GraylogUdpHandler()

    handler.send(_make_message(_make_record()))
    mock_sock.sendto.assert_called_once()
