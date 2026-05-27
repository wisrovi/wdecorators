Examples
========

Every decorator in wdecorators has a runnable example in the
``examples/`` directory. Below are a few key examples.

Performance: @benchmark
-----------------------

.. code-block:: python

    import time
    from wdecorators import benchmark

    @benchmark
    def slow_task():
        time.sleep(1)
        return "Completed"

    print(slow_task())

Resilience: @retry
------------------

.. code-block:: python

    import random
    from wdecorators import retry

    @retry(times=5)
    def may_fail():
        if random.random() < 0.5:
            raise ValueError("Random failure")
        return "Success!"

    print(may_fail())

Resilience: @timeout
--------------------

.. code-block:: python

    import time
    from wdecorators import timeout, TimeoutException

    @timeout(seconds=2)
    def long_task():
        time.sleep(5)

    try:
        long_task()
    except TimeoutException as e:
        print(f"Timeout: {e}")

Validation: @accepts
--------------------

.. code-block:: python

    from wdecorators import accepts

    @accepts(int, int)
    def add(a, b):
        return a + b

    print(add(3, 4))  # 7

Security: @sanitize_input
-------------------------

.. code-block:: python

    from wdecorators import sanitize_input

    @sanitize_input
    def display(message):
        return f"Message: {message}"

    print(display("<script>alert('XSS')</script>"))

Utilities: @singleton
---------------------

.. code-block:: python

    from wdecorators import singleton

    @singleton
    class Database:
        def __init__(self):
            print("Connecting...")

    db1 = Database()
    db2 = Database()
    print(db1 is db2)  # True

Flow Control: @run_once
-----------------------

.. code-block:: python

    from wdecorators import run_once

    @run_once
    def initialize():
        print("Initializing...")
        return "ready"

    print(initialize())  # Runs
    print(initialize())  # Cached

Graylog Logging
---------------

.. code-block:: python

    from wdecorators import init_logger, log_exceptions, logger

    init_logger("my_app", graylog_host="192.168.1.100")

    @log_exceptions()
    def process(order_id):
        logger.bind(send_to_graylog=True).info(f"Processing {order_id}")
        ...

Periodic Task Scheduler
-----------------------

.. code-block:: python

    from wdecorators import Periodic_task_sched

    controller = Periodic_task_sched()
    controller.set_database()

    @controller.periodic_execution(interval=5, priority="high")
    def critical():
        print("Critical task...")

    critical()
    controller.start_api()

Run All Examples
----------------

.. code-block:: bash

    for f in examples/*.py; do echo "=== $f ===" && python "$f"; done
