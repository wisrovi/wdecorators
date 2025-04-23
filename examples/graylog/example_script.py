from wdecorators import (
    init_logger,
    log_exceptions,
    log_execution_time,
    logger,
)


init_logger("demo_script", graylog_host="192.168.1.137", log_level="ERROR")


@log_execution_time(context={"send_to_graylog": True})
@log_exceptions(context={"tag": "critical_func", "send_to_graylog": True})
def demo():
    logger.bind(send_to_graylog=True).info("Ejemplo desde script Python")
    # logger.bind(send_to_graylog=True).exception(f"Exception in all")
    x = 1 / 0  # Provoca excepción


if __name__ == "__main__":
    demo()
