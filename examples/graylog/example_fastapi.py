# main.py

from fastapi import FastAPI, Request
from graylog_logger import init_logger, logger, log_exceptions

init_logger("fastapi_app")

app = FastAPI()


@app.get("/")
@log_exceptions()
def read_root():
    logger.bind(send_to_graylog=True).info("Petición GET a /")
    return {"message": "Hola desde FastAPI con Graylog"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
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


@app.get("/")
@log_exceptions(send_to_graylog=True)
def index():
    logger.bind(send_to_graylog=True).info("Welcome to FastAPI with Graylog")
    return {"msg": "OK"}


@app.get("/fail")
@log_exceptions(send_to_graylog=True)
def fail():
    return 1 / 0  # Will be logged to Graylog
