Development
===========

Setup
-----

.. code-block:: bash

    git clone https://github.com/wisrovi/wdecorators.git
    cd wdecorators
    pip install -e ".[scheduler]"
    pip install pytest pytest-asyncio isort black sphinx

Code Quality
------------

.. code-block:: bash

    isort .
    black .

Run tests:

.. code-block:: bash

    python -m pytest tests/ -v

Build docs:

.. code-block:: bash

    cd docs
    make html
    open _build/html/index.html

Release
-------

.. code-block:: bash

    python -m build
    twine upload dist/*
