.. _installation:

Installation
============

Spidermon's core functionality is pretty basic and it provides some features
that allow you to build your monitors on top of it. Spidermon doesn't have any
dependencies other than `six`. However, for most production projects you will
need some additional libraries in order to send notifications and to validate
the output data produced by Scrapy.

The recommended way to install the library is by adding the additional
`monitoring` and `validation` dependencies:

.. code-block:: bash

    pip install git+ssh://git@github.com/scrapinghub/spidermon.git#egg=spidermon[monitoring,validation]
