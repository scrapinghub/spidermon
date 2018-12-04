.. _actions:

=======
Actions
=======

By default, when a monitor suite finishes, the pass/fail information is included
in the spider logs, which would be enough during development but useless when
you are monitoring several spiders.

Spidermon allows you to define actions that are ran after the monitors finishes.
You can define your own actions or use one of the existing built-in actions.

.. _actions-email:

E-mail action
=============

This action relies on `Amazon Simple Email Service`_ to send an e-mail after the
monitor suite finishes its execution. In this example, an e-mail will be sent
when your monitor suite finishes no matter if it passed or failed:

.. code-block:: python

    from spidermon.contrib.actions.ses import SendSESEmail

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_finished_actions = [
            SendSESEmail,
        ]

By default, Spidermon uses a HTML template that can be altered in
:ref:`SPIDERMON_BODY_HTML_TEMPLATE` setting.

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

.. _SPIDERMON_AWS_ACCESS_KEY:

SPIDERMON_AWS_ACCESS_KEY
------------------------

.. _SPIDERMON_AWS_SECRET_KEY:

SPIDERMON_AWS_SECRET_KEY
------------------------

.. _SPIDERMON_EMAIL_SENDER:

SPIDERMON_EMAIL_SENDER
----------------------

.. _SPIDERMON_EMAIL_TO:

SPIDERMON_EMAIL_TO
------------------

The following settings can be used to improve the action:

.. _SPIDERMON_BODY_HTML:

SPIDERMON_BODY_HTML
-------------------

.. _SPIDERMON_BODY_HTML_TEMPLATE:

SPIDERMON_BODY_HTML_TEMPLATE
----------------------------

.. _SPIDERMON_BODY_TEXT:

SPIDERMON_BODY_TEXT
-------------------

.. _SPIDERMON_BODY_TEXT_TEMPLATE:

SPIDERMON_BODY_TEXT_TEMPLATE
----------------------------

.. _SPIDERMON_EMAIL_BCC:

SPIDERMON_EMAIL_BCC
-------------------

.. _SPIDERMON_EMAIL_CONTEXT:

SPIDERMON_EMAIL_CONTEXT
------------------

.. _SPIDERMON_EMAIL_CC:

SPIDERMON_EMAIL_CC
------------------

.. _SPIDERMON_EMAIL_FAKE:

SPIDERMON_EMAIL_FAKE
--------------------

.. _SPIDERMON_EMAIL_REPLY_TO:

SPIDERMON_EMAIL_REPLY_TO
------------------------

.. _SPIDERMON_EMAIL_SUBJECT:

SPIDERMON_EMAIL_SUBJECT
-----------------------

.. _SPIDERMON_EMAIL_SUBJECT_TEMPLATE:

SPIDERMON_EMAIL_SUBJECT_TEMPLATE
--------------------------------

.. _Amazon Simple Email Service: https://aws.amazon.com/pt/ses/

.. _actions-slack:

Slack action
============

.. _actions-job:

Job action
==========

.. _actions-report:

Report action
=============

.. _actions-custom-action:

Custom actions
==============
