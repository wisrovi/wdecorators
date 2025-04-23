import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
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
