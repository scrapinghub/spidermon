.. spidermon documentation master file, created by
   sphinx-quickstart on Tue Apr 21 21:43:18 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Spidermon's documentation!
=====================================

Spidermon is a framework to build monitors for Scrapy spiders. It offers the
following features:

* It can check the output data produced by Scrapy (or other sources) and
  verify it against a schema or model that defines the expected structure,
  data types and value restrictions. It supports data validation based on two
  external libraries:

  * jsonschema: `<https://github.com/Julian/jsonschema>`_
  * Schematics: `<https://github.com/schematics/schematics>`_
* It allows you to define conditions that should trigger an alert based on
  Scrapy stats.
* It supports notifications via email, Slack and Telegram.
* It can generate custom reports.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   getting-started
   monitors
   item-validation
   stats-collection
   expression-monitors
   settings
   configuring-slack-for-spidermon
   configuring-telegram-for-spidermon
   actions
   changelog
