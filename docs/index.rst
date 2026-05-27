.. wdecorators documentation master file.

wdecorators
============

**wdecorators** is a high-level Python decorator library with 40+ decorators
for performance profiling, resilience (retry, timeout, rate-limiting),
debugging, input sanitization, caching, validation, and task scheduling.

**Features:**
- **Performance** -- benchmark, profile memory, cache results
- **Resilience** -- retry, timeout, rate-limit, suppress errors
- **Debugging** -- trace calls, log arguments, count invocations
- **Validation** -- type checking, range/length validation
- **Security** -- sanitize input, mask sensitive data, auth checks
- **Utilities** -- singleton, periodic tasks, JSON conversion
- **Async** -- most decorators support both sync and async
- **Testing** -- 47+ unit tests with pytest

Quickstart
----------

.. code-block:: python

    from wdecorators import benchmark, retry, timeout, singleton

    @benchmark
    def slow_operation():
        ...

    @retry(times=3)
    def unreliable():
        ...

    @timeout(seconds=5)
    def must_finish():
        ...

Installation
------------

.. code-block:: bash

    pip install wdecorators

    # Optional extras
    pip install wdecorators[scheduler]  # Periodic task dashboard
    pip install wdecorators[graylog]    # Graylog FastAPI middleware

.. toctree::
   :maxdepth: 2
   :caption: Contents

   reference
   examples
   development

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
