"""FastAPI example with Graylog logging integration."""

from fastapi import FastAPI, Request

from wdecorators import init_logger, log_exceptions, logger

init_logger("fastapi_app")

app = FastAPI()


@app.get("/")
@log_exceptions()
def read_root():
    """Root endpoint with Graylog logging."""
    logger.bind(send_to_graylog=True).info("GET request to /")
    return {"message": "Hello from FastAPI with Graylog"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests and responses to Graylog."""
    logger.bind(send_to_graylog=True).info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.bind(send_to_graylog=True).info(
            f"Response status: {response.status_code}"
        )
        return response
    except Exception:
        logger.bind(send_to_graylog=True).exception("Unhandled error in request")
        raise


@app.get("/fail")
@log_exceptions()
def fail():
    """Endpoint that intentionally fails (demonstrates error logging)."""
    return 1 / 0  # Will be logged to Graylog
