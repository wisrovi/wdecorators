"""Tests for LoggingMiddleware."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from wdecorators.graylog.middleware import LoggingMiddleware


def test_dispatch_logs_request_and_response():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}

    with patch("wdecorators.graylog.middleware.logger") as mock_logger:
        mock_bind = MagicMock()
        mock_logger.bind.return_value = mock_bind

        client = TestClient(app)
        resp = client.get("/test")

        assert resp.status_code == 200
        assert resp.json() == {"message": "ok"}

        mock_logger.bind.assert_any_call(send_to_graylog=True)
        assert mock_bind.info.call_count == 2


def test_dispatch_logs_request_path_and_method():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.post("/api/data")
    async def create_data():
        return {"id": 1}

    with patch("wdecorators.graylog.middleware.logger") as mock_logger:
        mock_bind = MagicMock()
        mock_logger.bind.return_value = mock_bind

        client = TestClient(app)
        resp = client.post("/api/data", json={"name": "test"})

        assert resp.status_code == 200
        first_call = mock_bind.info.call_args_list[0]
        assert "POST" in first_call[0][0]
        assert "/api/data" in first_call[0][0]


def test_dispatch_logs_response_status_and_duration():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/status")
    async def status():
        return {"status": "ok"}

    with patch("wdecorators.graylog.middleware.logger") as mock_logger:
        mock_bind = MagicMock()
        mock_logger.bind.return_value = mock_bind

        client = TestClient(app)
        resp = client.get("/status")

        assert resp.status_code == 200
        second_call = mock_bind.info.call_args_list[1]
        assert "200" in second_call[0][0]
        assert "s" in second_call[0][0]


def test_dispatch_with_query_params():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/search")
    async def search(q: str = ""):
        return {"results": [q]}

    with patch("wdecorators.graylog.middleware.logger") as mock_logger:
        mock_bind = MagicMock()
        mock_logger.bind.return_value = mock_bind

        client = TestClient(app)
        resp = client.get("/search?q=hello")

        assert resp.status_code == 200
        assert resp.json() == {"results": ["hello"]}
        first_call = mock_bind.info.call_args_list[0]
        assert "q=hello" in first_call[0][0]


def test_dispatch_with_error_response():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/error")
    async def error():
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=500, content={"error": "server error"})

    with patch("wdecorators.graylog.middleware.logger") as mock_logger:
        mock_bind = MagicMock()
        mock_logger.bind.return_value = mock_bind

        client = TestClient(app)
        resp = client.get("/error")

        assert resp.status_code == 500
        second_call = mock_bind.info.call_args_list[1]
        assert "500" in second_call[0][0]


@pytest.mark.asyncio
async def test_dispatch_with_mocks():
    middleware = LoggingMiddleware(MagicMock())

    request = MagicMock()
    request.method = "GET"
    request.url = "http://test/hello"

    response = MagicMock()
    response.status_code = 200

    call_next = AsyncMock(return_value=response)

    with patch("wdecorators.graylog.middleware.logger") as mock_logger:
        mock_bind = MagicMock()
        mock_logger.bind.return_value = mock_bind

        result = await middleware.dispatch(request, call_next)

        assert result is response
        mock_logger.bind.assert_any_call(send_to_graylog=True)
        assert mock_bind.info.call_count == 2

        first_call = mock_bind.info.call_args_list[0]
        assert "GET" in first_call[0][0]

        second_call = mock_bind.info.call_args_list[1]
        assert "200" in second_call[0][0]
