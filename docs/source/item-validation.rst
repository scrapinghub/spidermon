.. _item-validation:

Item Validation
===============

One useful feature when monitoring a spider is being able to validate your returned items
against a defined schema.

Spidermon provides a mechanism that allows you to define an item schema and validation
rules that will be executed for each item returned. To enable item validation feature,
the first step is to enable the built-in item pipeline in your project settings:

.. code-block:: python

    # tutorial/settings.py
    ITEM_PIPELINES = {
        'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800,
    }

After that you need to choose which validation library will be used. Spidermon
accepts schemas defined using schematics_ or `JSON Schema`_.

With schematics
---------------

Schematics_ is a validation library based on ORM-like models. These models include
some common data types and validators, but they can also be extended to define
custom validation rules.

.. code-block:: python

    # Usually placed in validators.py file
    from schematics.models import Model
    from schematics.types import URLType, StringType, ListType

    class QuoteItem(Model):
        quote = StringType(required=True)
        author = StringType(required=True)
        author_url = URLType(required=True)
        tags = ListType(StringType)

Check the documentation to learn how to define a model and how to extend the
built-in data types.

With JSON Schema
----------------

`JSON Schema`_ is a powerful tool for validating the structure of JSON data. You can
define which fields are required, the type assigned to each field, a regular expression
to validate the content and much more.

This `guide`_ explains the main keywords and how to generate a schema.

Here we have an example of a schema for the quotes item from the :ref:`getting-started`.

.. code-block:: json

  /* validators/quotes.json */
  {
    "$schema": "http://json-schema.org/draft-04/schema",
    "type": "object",
    "properties": {
      "quote": {
        "type": "string"
      },
      "author": {
        "type": "string"
      },
      "author_url": {
        "type": "string",
        "pattern": ""
      },
      "tags": {
        "type"
      }
    },
    "required": [
      "quote",
      "author",
      "author_url"
    ]
  }

Settings
--------

These are the settings used for configuring item validation:

.. settings:: SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS

SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

When set, adds a field called `_validation` to the item that has validation errors.
You can change the name of the field changing :setting:`SPIDERMON_VALIDATION_ERRORS_FIELD`:

.. code-block:: json

    {
        '_validation': defaultdict(<class 'list'>, {'author_url': ['Invalid URL']}),
        'author': 'C.S. Lewis',
        'author_url': 'invalid_url',
        'quote': '“Some day you will be old enough to start reading fairy tales '
            'again.”',
        'tags': ['age', 'fairytales', 'growing-up']
    }

.. setting:: SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS

SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

Whether to drop items that contains validation errors.

.. setting:: SPIDERMON_VALIDATION_ERRORS_FIELD

SPIDERMON_VALIDATION_ERRORS_FIELD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``_validation``

The name of the field added to the item when a validation error happens and
:setting:`SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS` is enabled.

.. setting:: SPIDERMON_VALIDATION_MODELS

SPIDERMON_VALIDATION_MODELS
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

A `list` containing the models with th

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_MODELS: [
        'myproject.spiders.validators.DummyItemModel'
    ]

If you are working on a spider that produces multiple items types, you can define it
as a `dict`:

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_MODELS: {
        DummyItem: 'myproject.spiders.validators.DummyItemModel',
        OtherItem: 'myproject.spiders.validators.OtherItemModel',
    }

.. setting:: SPIDERMON_VALIDATION_SCHEMAS

SPIDERMON_VALIDATION_SCHEMAS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

A `list` containing the location of the item schema.

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_SCHEMAS: [
        '/path/to/schema.json',
    ]

If you are working on a spider that produces multiple items types, you can define it
as a `dict`:

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_SCHEMAS: {
        DummyItem: '/path/to/dummyitem_schema.json',
        OtherItem: '/path/to/otheritem_schema.json',
    }

.. _`schematics`: https://schematics.readthedocs.io/en/latest/
.. _`JSON Schema`: https://json-schema.org/
.. _`guide`: http://json-schema.org/learn/getting-started-step-by-step.html
