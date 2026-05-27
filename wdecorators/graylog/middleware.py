"""FastAPI middleware for request/response logging to Graylog."""

import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that logs all HTTP requests and responses to Graylog."""

    async def dispatch(self, request: Request, call_next):
        """Intercept and log each request/response pair.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware or route handler.

        Returns:
            HTTP response from the next handler.
        """
        start_time = time.time()
        logger.bind(send_to_graylog=True).info(
            f"Request: {request.method} {request.url}"
        )
        response = await call_next(request)
        duration = round(time.time() - start_time, 3)
        logger.bind(send_to_graylog=True).info(
            f"Response status: {response.status_code} in {duration}s"
        )
        return response
