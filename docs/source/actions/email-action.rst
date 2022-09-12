Email action
============

Spidermon provides two built-in actions that can be used to send email
reports in the configuration of a monitor suite.

- ``SendSESEmail`` uses `Amazon Simple Email Service`_ as the method to send your emails.
- ``SendSmtpEmail`` uses `SMTP`_  as the method to send your emails.

Basic usage of both actions are very similar. You just need to configure the desired
action in you monitor suite and configure a few specific settings depending on the
action you choose.

For example, to send an email report using `Amazon Simple Email Service`_ when
your ``DummyMonitorSuite`` finishes, you can use:

.. code-block:: python

    from spidermon.contrib.actions.email.ses import SendSESEmail

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_finished_actions = [
            SendSESEmail,
        ]

A second example, if you want to send an email report using `SMTP`_ when
your ``DummyMonitorSuite`` finishes and some monitor fails, you can use:

.. code-block:: python

    from spidermon.contrib.actions.email.smtp import SendSmtpEmail

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_failed_actions = [
            SendSmtpEmail,
        ]

By default Spidermon uses a HTML template that can be altered in
`SPIDERMON_BODY_HTML_TEMPLATE`_ setting. You can use `Jinja2`_ as your
template engine.

The result of a report generated using this default template may be seen next:

.. image:: /_static/email1.png
   :scale: 25 %
   :alt: Email Report 1

.. image:: /_static/email2.png
   :scale: 25 %
   :alt: Email Report 2

Available settings
------------------

The following settings are used by all email actions
(``SmtpSendEmail`` or ``SendSESEmail``).

SPIDERMON_EMAIL_SENDER
~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

Address of the sender of the email notification.

SPIDERMON_EMAIL_TO
~~~~~~~~~~~~~~~~~~

Default: ``None``

List of all recipients of the email notification.

The following settings can be used to improve the action:

SPIDERMON_BODY_HTML
~~~~~~~~~~~~~~~~~~~

Default: ``None``

SPIDERMON_BODY_HTML_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

String containing the location of the `Jinja2`_ template for the Spidermon email report.

Default :download:`reports/email/monitors/result.jinja <../../../spidermon/contrib/actions/reports/templates/reports/email/monitors/result.jinja>`.

SPIDERMON_BODY_TEXT
~~~~~~~~~~~~~~~~~~~

SPIDERMON_BODY_TEXT_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SPIDERMON_EMAIL_BCC
~~~~~~~~~~~~~~~~~~~

Default: ``None``

SPIDERMON_EMAIL_CONTEXT
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

SPIDERMON_EMAIL_CC
~~~~~~~~~~~~~~~~~~

Default: ``None``

SPIDERMON_EMAIL_FAKE
~~~~~~~~~~~~~~~~~~~~

Default: ``False``

If set `True`, the email content will be in the logs but no email will be sent.

SPIDERMON_EMAIL_REPLY_TO
~~~~~~~~~~~~~~~~~~~~~~~~

SPIDERMON_EMAIL_SUBJECT
~~~~~~~~~~~~~~~~~~~~~~~

SPIDERMON_EMAIL_SUBJECT_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Amazon SES action settings
--------------------------

The following settings are needed only if you are using ``SendSESEmail`` action.

SPIDERMON_AWS_ACCESS_KEY
~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

AWS Access Key.

.. warning::

    This setting has been deprecated in preference of ``SPIDERMON_AWS_ACCESS_KEY_ID``.

SPIDERMON_AWS_SECRET_KEY
~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

AWS Secret Key.

.. warning::

    This setting has been deprecated in preference of ``SPIDERMON_AWS_SECRET_ACCESS_KEY``.

SPIDERMON_AWS_ACCESS_KEY_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

AWS Access Key. If not set, it defaults to `AWS_ACCESS_KEY_ID`_ (``scrapy`` credentials for AWS S3 storage).

SPIDERMON_AWS_SECRET_ACCESS_KEY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default: ``None``

AWS Secret Key. If not set, it defaults to `AWS_SECRET_ACCESS_KEY`_ (``scrapy`` credentials for AWS S3 storage).

SPIDERMON_AWS_REGION_NAME
~~~~~~~~~~~~~~~~~~~~~~~~~

AWS Region.

Default: ``us-east-1``

SMTP action settings
--------------------

The following settings are needed only if you are using ``SmtpSendEmail`` action.

SPIDERMON_SMTP_HOST
~~~~~~~~~~~~~~~~~~~

The host of your `SMTP`_ server.

SPIDERMON_SMTP_PORT
~~~~~~~~~~~~~~~~~~~

The port of your `SMTP`_ server.

Default: ``25``

SPIDERMON_SMTP_USER
~~~~~~~~~~~~~~~~~~~

The user of your `SMTP`_ server.

SPIDERMON_SMTP_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~

The password of your `SMTP`_ server.

SPIDERMON_SMTP_ENFORCE_TLS
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enforce using SMTP STARTTLS.

Default: ``False``

SPIDERMON_SMTP_ENFORCE_SSL
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enforce using a secure SSL connection.

Default: ``False``

.. _Amazon Simple Email Service: https://aws.amazon.com/pt/ses/
.. _`AWS_ACCESS_KEY_ID`: https://docs.scrapy.org/en/latest/topics/settings.html#aws-access-key-id
.. _`AWS_SECRET_ACCESS_KEY`: https://docs.scrapy.org/en/latest/topics/settings.html#aws-secret-access-key
.. _Jinja2: http://jinja.pocoo.org/
.. _SMTP: https://datatracker.ietf.org/doc/html/rfc821