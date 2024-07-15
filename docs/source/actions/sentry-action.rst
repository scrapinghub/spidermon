Sentry action
=============

This action allows you to send custom messages to `Sentry`_ when your
monitor suites finish their execution. To use this action
you need to provide the `Sentry DSN`_ in your `settings.py`
file as follows:

.. code-block:: python

    # settings.py
    SPIDERMON_SENTRY_DSN = '<SENTRY_DSN_URL>'
    SPIDERMON_SENTRY_PROJECT_NAME = '<PROJECT_NAME>'
    SPIDERMON_SENTRY_ENVIRONMENT_TYPE = '<ENVIRONMENT_TYPE>'

A notification on `Sentry`_ will look like the following one:

.. image:: /_static/sentry_notification.png
   :scale: 50 %
   :alt: Sentry Notification

The message will have tags based on the failed monitor names (after replacing
whitespace, special symbols etc.), but as the tag length is limited to 32 chars
you should use ``@monitors.name`` to set monitor names that will produce useful
tag names.

The following settings are needed to make this action workable:

SPIDERMON_SENTRY_DSN
--------------------------

Data Source Name provided by `Sentry`_, it's a representation of the configuration required by the Sentry SDKs.

SPIDERMON_SENTRY_PROJECT_NAME
-------------------------------------

Project name to use in notification title.

SPIDERMON_SENTRY_ENVIRONMENT_TYPE
-------------------------------------

Default: ``Development``

Environment type to use in notification title.
It could be set to anything like local, staging, development or production.

SPIDERMON_SENTRY_LOG_LEVEL
---------------------------

Default: ``error``

SPIDERMON_SENTRY_FAKE
---------------------

Default: ``False``

If set `True`, the Sentry message will be in the logs but nothing will be sent.

.. _`Sentry`: https://sentry.io/
.. _`Sentry DSN`: https://docs.sentry.io/concepts/key-terms/dsn-explainer/#dsn-utilization
