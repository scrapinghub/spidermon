.. _installation:

Installation
============

Spidermon's core functionality provides some useful features that allow you to
build your monitors on top of it. The library depends on jsonschema_ and
`python-slugify`_.

If you want to set up any notifications, additional `monitoring` dependencies will help with that.

If you want to use schematics_ validation, you probably want `validation`.

So the recommended way to install the library is by adding both:

.. code-block:: bash

    pip install "spidermon[monitoring,validation]"


.. _`jsonschema`: https://pypi.org/project/jsonschema/
.. _`python-slugify`: https://pypi.org/project/python-slugify/
.. _`schematics`: https://pypi.org/project/schematics/
