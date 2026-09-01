"""Tests for graylog logger init, log_exceptions, and log_execution_time."""

import os
from unittest.mock import patch

import pytest
from loguru import logger

from wdecorators.graylog.loggerg import init_logger, log_exceptions, log_execution_time


class TestInitLogger:
    def setup_method(self):
        logger.remove()

    @patch("wdecorators.graylog.loggerg.logger.add")
    @patch("wdecorators.graylog.loggerg.logger.remove")
    def test_init_with_env_host(self, mock_remove, mock_add):
        with patch.dict(
            os.environ, {"GRAYLOG_HOST": "graylog.example.com"}, clear=True
        ):
            result = init_logger(log_name="myapp")
            assert result is logger
            graylog_add = [
                c for c in mock_add.call_args_list if "GraylogUdpHandler" in str(c)
            ]
            assert len(graylog_add) == 1
            handler = graylog_add[0][0][0]
            assert handler.address == ("graylog.example.com", 12201)

    @patch("wdecorators.graylog.loggerg.logger.add")
    @patch("wdecorators.graylog.loggerg.logger.remove")
    def test_init_with_param_host(self, mock_remove, mock_add):
        with patch.dict(os.environ, {}, clear=True):
            result = init_logger(graylog_host="10.0.0.50", log_name="myapp")
            assert result is logger
            graylog_add = [
                c for c in mock_add.call_args_list if "GraylogUdpHandler" in str(c)
            ]
            assert len(graylog_add) == 1
            handler = graylog_add[0][0][0]
            assert handler.address == ("127.0.0.1", 12201)

    @patch("wdecorators.graylog.loggerg.logger.add")
    @patch("wdecorators.graylog.loggerg.logger.remove")
    def test_init_no_host_skips_graylog(self, mock_remove, mock_add):
        with patch.dict(os.environ, {}, clear=True):
            init_logger()
            graylog_add = [
                c for c in mock_add.call_args_list if "GraylogUdpHandler" in str(c)
            ]
            assert len(graylog_add) == 0

    @patch("wdecorators.graylog.loggerg.logger.add")
    @patch("wdecorators.graylog.loggerg.logger.remove")
    def test_init_with_env_port(self, mock_remove, mock_add):
        with patch.dict(
            os.environ, {"GRAYLOG_HOST": "host", "GRAYLOG_PORT": "12345"}, clear=True
        ):
            init_logger()
            graylog_add = [
                c for c in mock_add.call_args_list if "GraylogUdpHandler" in str(c)
            ]
            handler = graylog_add[0][0][0]
            assert handler.address == ("host", 12345)

    @patch("wdecorators.graylog.loggerg.logger.add")
    @patch("wdecorators.graylog.loggerg.logger.remove")
    def test_init_dev_env_adds_file_sink(self, mock_remove, mock_add):
        with patch.dict(
            os.environ, {"GRAYLOG_HOST": "host", "APP_ENV": "dev"}, clear=True
        ):
            init_logger()
            file_add = [c for c in mock_add.call_args_list if "logs/dev.log" in str(c)]
            assert len(file_add) == 1

    @patch("wdecorators.graylog.loggerg.logger.add")
    @patch("wdecorators.graylog.loggerg.logger.remove")
    def test_init_non_dev_skips_file_sink(self, mock_remove, mock_add):
        with patch.dict(
            os.environ, {"GRAYLOG_HOST": "host", "APP_ENV": "production"}, clear=True
        ):
            init_logger()
            file_add = [c for c in mock_add.call_args_list if "logs/dev.log" in str(c)]
            assert len(file_add) == 0


class TestLogExceptions:
    def test_no_exception_returns_result(self):
        @log_exceptions()
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    def test_exception_caught_no_raise(self):
        @log_exceptions()
        def crash():
            raise ValueError("boom")

        assert crash() is None

    def test_exception_caught_with_raise(self):
        @log_exceptions(enable_raise=True)
        def crash():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            crash()

    def test_custom_context(self):
        @log_exceptions(context={"send_to_graylog": True, "user_id": "test"})
        def ok():
            return 42

        assert ok() == 42

    def test_exception_logs_without_raise_custom_context(self):
        @log_exceptions(
            context={"send_to_graylog": True, "user_id": "test"}, enable_raise=False
        )
        def crash():
            raise RuntimeError("fail")

        assert crash() is None

    @pytest.mark.asyncio
    async def test_async_function_returns_coroutine(self):
        @log_exceptions()
        async def fetch():
            return "data"

        result = await fetch()
        assert result == "data"

    @pytest.mark.asyncio
    async def test_async_exception_caught(self):
        @log_exceptions()
        async def crash():
            raise KeyError("missing")

        with pytest.raises(KeyError, match="missing"):
            await crash()


class TestLogExecutionTime:
    def test_sync_logs_execution_time(self):
        @log_execution_time()
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    def test_with_custom_context(self):
        @log_execution_time(context={"send_to_graylog": True, "user_id": "u1"})
        def greet(name):
            return f"Hello {name}"

        assert greet("World") == "Hello World"

    def test_default_context(self):
        @log_execution_time()
        def identity(x):
            return x

        assert identity(42) == 42

    @pytest.mark.asyncio
    async def test_async_function(self):
        @log_execution_time()
        async def fetch():
            return "data"

        result = await fetch()
        assert result == "data"

    @pytest.mark.asyncio
    async def test_async_with_custom_context(self):
        @log_execution_time(context={"send_to_graylog": True})
        async def compute(x):
            return x * 2

        result = await compute(21)
        assert result == 42
