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

Default: ``None``

AWS Access Key.

.. _SPIDERMON_AWS_SECRET_KEY:

SPIDERMON_AWS_SECRET_KEY
------------------------

AWS Secret Key.

Default: ``None``

.. _SPIDERMON_EMAIL_SENDER:

SPIDERMON_EMAIL_SENDER
----------------------

Default: ``None``

Address of the sender of the e-mail notification.

.. _SPIDERMON_EMAIL_TO:

SPIDERMON_EMAIL_TO
------------------

Default: ``None``

List of all recipients of the e-mail notification.

The following settings can be used to improve the action:

.. _SPIDERMON_BODY_HTML:

SPIDERMON_BODY_HTML
-------------------

Default: ``None``

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

Default: ``None``

.. _SPIDERMON_EMAIL_CONTEXT:

SPIDERMON_EMAIL_CONTEXT
------------------

Default: ``None``

.. _SPIDERMON_EMAIL_CC:

SPIDERMON_EMAIL_CC
------------------

Default: ``None``

.. _SPIDERMON_EMAIL_FAKE:

SPIDERMON_EMAIL_FAKE
--------------------

Default: ``False``

If set will output the e-mail content in the logs and don't send it.

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

.. _SPIDERMON_SLACK_ATTACHMENTS

SPIDERMON_SLACK_ATTACHMENTS
---------------------------

.. _SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE

SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE
------------------------------------

.. _SPIDERMON_SLACK_FAKE

SPIDERMON_SLACK_FAKE
--------------------

.. _SPIDERMON_SLACK_INCLUDE_ATTACHMENTS

SPIDERMON_SLACK_INCLUDE_ATTACHMENTS
-----------------------------------

.. _SPIDERMON_SLACK_INCLUDE_MESSAGE

SPIDERMON_SLACK_INCLUDE_MESSAGE
-------------------------------

.. _SPIDERMON_SLACK_MESSAGE

SPIDERMON_SLACK_MESSAGE
-----------------------

.. _SPIDERMON_SLACK_MESSAGE_TEMPLATE

SPIDERMON_SLACK_MESSAGE_TEMPLATE
--------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS

SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS
--------------------------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS

SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS
-----------------------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK

SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK
--------------------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX

SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX
-------------------------------------

.. _SPIDERMON_SLACK_RECIPIENTS

SPIDERMON_SLACK_RECIPIENTS
--------------------------

.. _SPIDERMON_SLACK_SENDER_NAME

SPIDERMON_SLACK_SENDER_NAME
---------------------------

.. _SPIDERMON_SLACK_SENDER_TOKEN

SPIDERMON_SLACK_SENDER_TOKEN
----------------------------

.. _actions-job-tags:

Job tags action
===============

If you are running your spider using the `Scrapy Cloud`_ you are able to include
tags in your jobs. Spidermon includes two actions that may be used to add or to
remove tags to your jobs depending on the result of the monitoring.

In this example, considering that you defined a `running` tag when you start the
job in `Scrapy Cloud`_, if the job passes without errors, it will remove this tag.
If the job fails the `failed` tag will be added to the job so you can easily look
for failed jobs.

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.jobs.tags import AddJobTags, RemoveJobTags

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_passed_actions = [
            RemoveJobTags,
        ]

        monitors_failed_actions = [
            AddJobTags,
        ]

.. code-block:: python

    # settings.py
    SPIDERMON_JOB_TAGS_TO_ADD = ['failed', ]
    SPIDERMON_JOB_TAGS_TO_REMOVE = ['running', ]

By default we have the following settings when using these two actions:

.. _SPIDERMON_JOB_TAGS_TO_ADD

SPIDERMON_JOB_TAGS_TO_ADD
----------------------

List of tags to be included when `AddJobTags` is executed.

.. _SPIDERMON_JOB_TAGS_TO_REMOVE

SPIDERMON_JOB_TAGS_TO_REMOVE
----------------------

List of tags to be removed when `RemoveJobTags` is executed.

If you want to have different rules adding or removing tags for different results
of the monitoring, you need to create a custom action class including the name
of the setting that will contain the list of tags that will be included in the job:

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.jobs.tags import AddJobTags

    class AddJobTagsPassed(AddJobTags):
        tag_settings = 'TAG_TO_ADD_WHEN_PASS'

    class AddJobTagsFailed(AddJobTags):
        tag_settings = 'TAG_TO_ADD_WHEN_FAIL'

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_passed_actions = [
            AddJobTagsPassed,
        ]

        monitors_failed_actions = [
            AddJobTagsFailed,
        ]

.. code-block:: python

    # settings.py
    TAG_TO_ADD_WHEN_PASS = ['passed', ]
    TAG_TO_ADD_WHEN_FAIL = ['failed', ]

.. _Scrapy Cloud: https://scrapinghub.com/scrapy-cloud

.. _actions-file-report:

File Report action
==================

.. _actions-s3-report:

S3 Report action
================

.. _actions-custom-action:

Custom actions
==============
