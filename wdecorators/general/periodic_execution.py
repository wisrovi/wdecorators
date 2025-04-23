import time
import functools
import threading


def periodic_execution(interval):
    """
    Ejecuta la función de forma periódica cada 'interval' segundos.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def run():
                while True:
                    func(*args, **kwargs)
                    time.sleep(interval)

            thread = threading.Thread(
                target=run,
                # daemon=True,
            )
            thread.start()
            return thread  # Retorna el hilo para control externo si es necesario

        return wrapper

    return decorator


@periodic_execution(5)
def say_hello():
    print("Hola, esto se ejecuta cada 5 segundos")


say_hello()
