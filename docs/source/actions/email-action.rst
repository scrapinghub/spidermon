E-mail action
=============

This action relies on `Amazon Simple Email Service`_ to send an e-mail after the
monitor suite finishes its execution. In this example, an e-mail will be sent
when your monitor suite finishes no matter if it passed or failed:

.. code-block:: python

    from spidermon.contrib.actions.email.ses import SendSESEmail

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_finished_actions = [
            SendSESEmail,
        ]

By default, Spidermon uses a HTML template that can be altered in
`SPIDERMON_BODY_HTML_TEMPLATE`_ setting. You can use `Jinja2`_ as your
template engine.

The result of a report generated using this default template may be seen next:

.. image:: /_static/email1.png
   :scale: 25 %
   :alt: E-mail Report 1

.. image:: /_static/email2.png
   :scale: 25 %
   :alt: E-mail Report 2

You can also define actions for when your monitors fails or passes also including
actions to the lists `monitors_passed_actions` and `monitors_failed_actions`.

The following settings are the minimum needed to make this action works:

SPIDERMON_AWS_ACCESS_KEY
------------------------

Default: ``None``

AWS Access Key.

.. warning::

    This setting has been deprecated in preference of ``SPIDERMON_AWS_ACCESS_KEY_ID``.

SPIDERMON_AWS_SECRET_KEY
------------------------

Default: ``None``

AWS Secret Key.

.. warning::

    This setting has been deprecated in preference of ``SPIDERMON_AWS_SECRET_ACCESS_KEY``.

SPIDERMON_AWS_ACCESS_KEY_ID
---------------------------

Default: ``None``

AWS Access Key. If not set, it defaults to `AWS_ACCESS_KEY_ID`_ (``scrapy`` credentials for AWS S3 storage).

SPIDERMON_AWS_SECRET_ACCESS_KEY
-------------------------------

Default: ``None``

AWS Secret Key. If not set, it defaults to `AWS_SECRET_ACCESS_KEY`_ (``scrapy`` credentials for AWS S3 storage).

SPIDERMON_AWS_REGION_NAME
-------------------------

AWS Region.

Default: ``us-east-1``

SPIDERMON_EMAIL_SENDER
----------------------

Default: ``None``

Address of the sender of the e-mail notification.

SPIDERMON_EMAIL_TO
------------------

Default: ``None``

List of all recipients of the e-mail notification.

The following settings can be used to improve the action:

SPIDERMON_BODY_HTML
-------------------

Default: ``None``

SPIDERMON_BODY_HTML_TEMPLATE
----------------------------

String containing the location of the `Jinja2`_ template for the Spidermon email report.

Default :download:`reports/email/monitors/result.jinja <../../../spidermon/contrib/actions/reports/templates/reports/email/monitors/result.jinja>`.

SPIDERMON_BODY_TEXT
-------------------

SPIDERMON_BODY_TEXT_TEMPLATE
----------------------------

SPIDERMON_EMAIL_BCC
-------------------

Default: ``None``

SPIDERMON_EMAIL_CONTEXT
-----------------------

Default: ``None``

SPIDERMON_EMAIL_CC
------------------

Default: ``None``

SPIDERMON_EMAIL_FAKE
--------------------

Default: ``False``

If set `True`, the e-mail content will be in the logs but no e-mail will be sent.

SPIDERMON_EMAIL_REPLY_TO
------------------------

SPIDERMON_EMAIL_SUBJECT
-----------------------

SPIDERMON_EMAIL_SUBJECT_TEMPLATE
--------------------------------

.. _Amazon Simple Email Service: https://aws.amazon.com/pt/ses/
.. _`AWS_ACCESS_KEY_ID`: https://docs.scrapy.org/en/latest/topics/settings.html#aws-access-key-id
.. _`AWS_SECRET_ACCESS_KEY`: https://docs.scrapy.org/en/latest/topics/settings.html#aws-secret-access-key
.. _Jinja2: http://jinja.pocoo.org/
