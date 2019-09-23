==========
Habraproxy
==========

.. image:: https://img.shields.io/badge/style-wemake-000000.svg
    :target: https://github.com/wemake-services/wemake-python-styleguide
    :alt: wemake.services code style

Proxy for https://habr.com that shows content from this site, but modifies pages so that after each 6-symbols word ™
sign is added.

Things that were not implemented:

* Form submitting most likely will return 4** or 5** responses in most cases.
* Some static files may be missing.
* Some ad banners and other services integrations may not work at all or be displayed incorrectly.

Free software: MIT license

Getting started
---------------

Initial project setup
^^^^^^^^^^^^^^^^^^^^^
Prerequisites: Python 3.6 and, optionally, Docker

Make these commands from project root:

.. code:: bash

  make virtualenv
  source env/bin/activate
  make requirements
  pre-commit install

After that you may run an app with ``FLASK_APP=habraproxy/app.py FLASK_ENV=development flask run``.

Alternatively, you may run the application with Docker:

.. code:: bash

    docker build . -t habraproxy
    docker run --rm -d --name habraproxy -p 5000:5000 habraproxy flask run --host=0.0.0.0 --port=5000

Updating requirements
^^^^^^^^^^^^^^^^^^^^^
Project uses `pip-tools
<https://github.com/jazzband/pip-tools>`_ for requirements management. If you need to add a new requirement, go to
``requirements`` directory and change the corresponding \*.in file. After that call ``make requirements`` to
compile \*.txt files and synchronize local environment.

For requirements installation in CI or production environments it is enough to simply call ``pip install -r
requirements/<file_name>.txt``.

For compatibility with traditional project structure there is also ``requirements.txt`` file at project root, which
simply links to ``requirements/production.txt``.

Linting
^^^^^^^

EditorConfig
============
There is ``.editorconfig`` file at the project root, which describes some basic rules for IDE. PyCharm supports it out
of the box, for other IDEs you may have to install a plugin.

Visit https://editorconfig.org/ for additional information.

Commit hooks
============
You may run linters after every commit so that they prevent committing code that has some problems. To do this, execute
``pre-commit install``.

This will install all hooks, described at configuration file ``.pre-commit-config.yaml``.

If you wish to run all checks manually, execute ``pre-commit run --all-files`` (or ``make lint``).
For running only a single specific check use ``pre-commit run <hook_id> --all-files`` (you can find hook id of the
desired check at ``.pre-commit-config.yaml``).

Note that ``pre-commit`` checks only files that are tracked by ``git``.

You can find tool documentation at https://pre-commit.com/.

Tests
^^^^^

Project uses ``pytest`` for testing.

All tests should be placed inside ``tests/`` directory and (ideally) follow the project structure - for example, tests
for ``habraproxy.some_package.some_module`` should be located at
``tests/some_package/test_some_module.py``

For assertions either default python's ``assert`` can be used, or more specific assertions from PyHamcrest_ - may be
useful for complex assertions and just more readable.

.. _PyHamcrest: https://pyhamcrest.readthedocs.io/en/release-1.8/library/

To run tests: ``make test``.
To run tests and receive a coverage statistics: ``make coverage``.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
