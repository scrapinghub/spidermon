Description
===========

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
* It supports notifications via email and Slack.
* It can generate custom reports.
