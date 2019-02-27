.. _installation:

Installation
============

Spidermon's core functionality provides some useful features that allow you to build your monitors on top of it. The library depends on `six`, `jsonschema` and `python-slugify`.
If you want to set up any notifications, additional `monitoring` dependencies will help with that.
If you want to use `schematics` validation, you probably want `validation`.

So the recommended way to install the library is by adding both:

.. code-block:: bash

    pip install "spidermon[monitoring,validation]"
