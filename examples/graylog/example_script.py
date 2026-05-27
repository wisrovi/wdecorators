"""Script example demonstrating Graylog logging decorators."""

from wdecorators import init_logger, log_exceptions, log_execution_time, logger

init_logger("demo_script", graylog_host="192.168.1.137", log_level="ERROR")


@log_execution_time(context={"send_to_graylog": True})
@log_exceptions(context={"tag": "critical_func", "send_to_graylog": True})
def demo():
    """Demo function that logs to Graylog and triggers an exception."""
    logger.bind(send_to_graylog=True).info("Example from Python script")
    1 / 0  # Triggers ZeroDivisionError


if __name__ == "__main__":
    demo()
