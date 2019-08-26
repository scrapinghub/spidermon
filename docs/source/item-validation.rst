.. _item-validation:

Item Validation
===============

One useful feature when monitoring a spider is being able to validate your returned items
against a defined schema.

Spidermon provides a mechanism that allows you to define an item schema and validation
rules that will be executed for each item returned. To enable the item validation feature,
the first step is to enable the built-in item pipeline in your project settings:

.. code-block:: python

    # tutorial/settings.py
    ITEM_PIPELINES = {
        'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800,
    }

After that, you need to choose which validation library will be used. Spidermon
accepts schemas defined using schematics_, `JSON Schema`_ or cerberus_.

With schematics
---------------

Schematics_ is a validation library based on ORM-like models. These models include
some common data types and validators, but they can also be extended to define
custom validation rules.

.. warning::

   You need to install `schematics`_ to use this feature.

.. code-block:: python

    # Usually placed in validators.py file
    from schematics.models import Model
    from schematics.types import URLType, StringType, ListType

    class QuoteItem(Model):
        quote = StringType(required=True)
        author = StringType(required=True)
        author_url = URLType(required=True)
        tags = ListType(StringType)

Check `schematics documentation`_ to learn how to define a model and how to extend the
built-in data types.

With JSON Schema
----------------

`JSON Schema`_ is a powerful tool for validating the structure of JSON data. You can
define which fields are required, the type assigned to each field, a regular expression
to validate the content and much more.

.. warning::

   You need to install `jsonschema`_ to use this feature.

This `guide`_ explains the main keywords and how to generate a schema. Here we have
an example of a schema for the quotes item from the :doc:`tutorial </getting-started>`.

.. code-block:: json

  {
    "$schema": "http://json-schema.org/draft-07/schema",
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

With Cerberus
-------------

`Cerberus`_ is a powerful yet simple and lightweight data validation
tool, designed to be ​extensible​, allowing for custom validation​ and has ​no
dependencies. You can define what the field contains, what is required, the type of
each field, as well as dependencies and regex.

.. warning::

   You need to install `cerberus`_ to use this feature.

This `usage`_ and `validation-rules`_ guide explain the main keywords and how to make a
schema. Here we have an example of a schema for the quotes item from the
:doc:`tutorial </getting-started>`.

.. code-block:: json

    {
        "quote": {"type": "string", "required": true},
        "author": {"type": "string", "required": true},
        "author_url": {"type": "string"},
        "tags": {"type": "list"}
    }

To use Cerberus validation, you would need to add
:ref:`SPIDERMON_VALIDATION_CERBERUS` setting to your `settings.py`

Settings
--------

These are the settings used for configuring item validation:

.. _SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS:

SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

When set to ``True``, this adds a field called `_validation` to the item that contains any validation errors.
You can change the name of the field by assigning a name to :ref:`SPIDERMON_VALIDATION_ERRORS_FIELD`:

.. code-block:: python

    {
        '_validation': defaultdict(<class 'list'>, {'author_url': ['Invalid URL']}),
        'author': 'C.S. Lewis',
        'author_url': 'invalid_url',
        'quote': 'Some day you will be old enough to start reading fairy tales '
            'again.',
        'tags': ['age', 'fairytales', 'growing-up']
    }

.. _SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS:

SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

Whether to drop items that contain validation errors.

.. _SPIDERMON_VALIDATION_ERRORS_FIELD:

SPIDERMON_VALIDATION_ERRORS_FIELD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``_validation``

The name of the field added to the item when a validation error happens and
:ref:`SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS` is enabled.

.. _SPIDERMON_VALIDATION_MODELS:

SPIDERMON_VALIDATION_MODELS
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

A `list` containing the `schematics models`_ that contain the definition of the items
that need to be validated.

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_MODELS: [
        'myproject.validators.DummyItemModel'
    ]

If you are working on a spider that produces multiple items types, you can define it
as a `dict`:

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_MODELS: {
        DummyItem: 'myproject.validators.DummyItemModel',
        OtherItem: 'myproject.validators.OtherItemModel',
    }

.. _SPIDERMON_VALIDATION_SCHEMAS:

SPIDERMON_VALIDATION_SCHEMAS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

A `list` containing the location of the item schema. Could be a local path or a URL.

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_SCHEMAS: [
        '/path/to/schema.json',
        's3://bucket/schema.json',
        'https://example.com/schema.json',
    ]

If you are working on a spider that produces multiple items types, you can define it
as a `dict`:

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_SCHEMAS: {
        DummyItem: '/path/to/dummyitem_schema.json',
        OtherItem: '/path/to/otheritem_schema.json',
    }

.. _SPIDERMON_VALIDATION_CERBERUS:

SPIDERMON_VALIDATION_CERBERUS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

A `list` containing the local path of the item schema.

.. code-block:: python

    # settings.py

    SPIDERMON_VALIDATION_CERBERUS = [
        '/path/to/schema.json',
        'http://example.com/mycerberusschema',
        {"Field": {"type": "number", "required":True}}
    ]

If you are working on a spider that produces multiple items types, you can define paths to schema for each item as `dict` as shown below:

    # settings.py

    from quotes.items import DummyItem, OtherItem

    SPIDERMON_VALIDATION_CERBERUS = {
        DummyItem: '/path/to/dummyitem_schema.json',
        OtherItem: '/path/to/otheritem_schema.json',
    }

Validation in Monitors
----------------------

You can build a monitor that checks the validation problems and raises errors if there are too many.
You can base it on ``spidermon.contrib.monitors.mixins.ValidationMonitorMixin`` which provides methods
that can be useful for this. There are 2 groups of methods, for checking all validation errors and
specifically for checking ``missing_required_field`` errors. All of these methods rely on the job stats,
reading ``spidermon/validation/fields/errors/*`` entries.

* ``check_missing_required_fields``, ``check_missing_required_field`` - check that number of
  ``missing_required_field`` errors is less than the specified threshold.
* ``check_missing_required_fields_percent``, ``check_missing_required_field_percent`` -  check that
  percent of ``missing_required_field`` errors is less than the specified threshold.
* ``check_fields_errors``, ``check_field_errors`` - check that the number of specified (or all) errors
  is less than the specified threshold.
* ``check_fields_errors_percent``, ``check_field_errors_percent`` - check that the percent of specified
  (or all) errors is less than the specified threshold.

All ``*_field`` method take a name of one field, while all ``*_fields`` method take a list of field names.

.. warning:: The default behavior for ``*_fields`` methods when no field names is passed is to combine
 error counts for all fields instead of checking each field separately. This is usually not very useful
 and inconsistent with the behavior when a list of fields is passed, so you should set the
 ``correct_field_list_handling`` monitor attribute to get the correct behavior. This will be the default
 in some later version.

Some examples:

.. code-block:: python

    # checks that each of field2 and field3 is missing in no more than 10 items
    self.check_missing_required_fields(field_names=['field2', 'field3'], allowed_count=10)

    # checks that field2 has errors in no more than 15% of items
    self.check_field_errors_percent(field_name='field2', allowed_percent=15)

    # checks that no errors is present in any fields
    self.check_field_errors_percent()

.. _`cerberus`: https://pypi.org/project/Cerberus/
.. _`guide`: http://json-schema.org/learn/getting-started-step-by-step.html
.. _`jsonschema`: https://pypi.org/project/jsonschema/
.. _`JSON Schema`: https://json-schema.org/
.. _`schematics`: https://schematics.readthedocs.io/en/latest/
.. _`schematics documentation`: https://schematics.readthedocs.io/en/latest/
.. _`schematics models`: https://schematics.readthedocs.io/en/latest/usage/models.html
.. _`usage`: http://docs.python-cerberus.org/en/latest/usage.html
.. _`validation-rules`: http://docs.python-cerberus.org/en/latest/validation-rules.html
