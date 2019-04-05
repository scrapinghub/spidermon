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
:ref:`SPIDERMON_BODY_HTML_TEMPLATE` setting. You can use `Jinja2`_ as your
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
-----------------------

Default: ``None``

.. _SPIDERMON_EMAIL_CC:

SPIDERMON_EMAIL_CC
------------------

Default: ``None``

.. _SPIDERMON_EMAIL_FAKE:

SPIDERMON_EMAIL_FAKE
--------------------

Default: ``False``

If set `True`, the e-mail content will be in the logs but no e-mail will be sent.

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
.. _Jinja2: http://jinja.pocoo.org/

.. _actions-slack:

Slack action
============

This action allows you to send custom messages to a `Slack`_ channel (or user)
using a bot when your monitor suites finishes their execution. To use this action
you need to provide the `Slack credentials`_ in your `settings.py`
file as follows:

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = '<SLACK_SENDER_TOKEN>'
    SPIDERMON_SLACK_SENDER_NAME = '<SLACK_SENDER_NAME>'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']

A notification will look like the following one:

.. image:: /_static/slack_notification.png
   :scale: 50 %
   :alt: Slack Notification

The following settings are the minimum needed to make this action works:

.. _SPIDERMON_SLACK_RECIPIENTS:

SPIDERMON_SLACK_RECIPIENTS
--------------------------

List of recipients of the message. It could be a channel or an user.

.. _SPIDERMON_SLACK_SENDER_NAME:

SPIDERMON_SLACK_SENDER_NAME
---------------------------
Name of app/bot/user created for serving notifications on desired channels.

.. _SPIDERMON_SLACK_SENDER_TOKEN:

SPIDERMON_SLACK_SENDER_TOKEN
----------------------------

Read `here`_ to know more about Slack Tokens.
Get your Slack Credentials by `creating an app <https://api.slack.com/apps>`_  here.

The `SPIDERMON_SLACK_SENDER_TOKEN` is the `API Token` available in your Slack application dashboard. You can navigate to Browse apps> Custom Integrations > Bots > Edit Configuration. 

Warning: Be careful when using bot user tokens in Spidermon. Do not publish bot user tokens in public code repositories.

Other settings available:

.. _SPIDERMON_SLACK_ATTACHMENTS:

SPIDERMON_SLACK_ATTACHMENTS
---------------------------

.. _SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE:

SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE
------------------------------------

.. _SPIDERMON_SLACK_FAKE:

SPIDERMON_SLACK_FAKE
--------------------

Default: ``False``

If set `True`, the Slack message content will be in the logs but nothing will be sent.

.. _SPIDERMON_SLACK_INCLUDE_ATTACHMENTS:

SPIDERMON_SLACK_INCLUDE_ATTACHMENTS
-----------------------------------

.. _SPIDERMON_SLACK_INCLUDE_MESSAGE:

SPIDERMON_SLACK_INCLUDE_MESSAGE
-------------------------------

.. _SPIDERMON_SLACK_MESSAGE:

SPIDERMON_SLACK_MESSAGE
-----------------------

.. _SPIDERMON_SLACK_MESSAGE_TEMPLATE:

SPIDERMON_SLACK_MESSAGE_TEMPLATE
--------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS:

SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS
--------------------------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS:

SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS
-----------------------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK:

SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK
--------------------------------------------

.. _SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX:

SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX
-------------------------------------

.. _`Slack`: https://slack.com/
.. _`Slack credentials`: https://api.slack.com/docs/token-types
.. _`here`: https://api.slack.com/docs/token-types

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

.. _SPIDERMON_JOB_TAGS_TO_ADD:

SPIDERMON_JOB_TAGS_TO_ADD
-------------------------

List of tags to be included when `AddJobTags` is executed.

.. _SPIDERMON_JOB_TAGS_TO_REMOVE:

SPIDERMON_JOB_TAGS_TO_REMOVE
----------------------------

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

This action allows to create a file report based on a template. As
:ref:`actions-email` you can use `Jinja2`_ as your template engine.

In this example we will create a file called `my_report.html` when the monitor suite finishes:

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.reports.files import CreateFileReport

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_finished_actions = [
            CreateFileReport,
        ]

.. code-block:: python

    # settings.py
    SPIDERMON_REPORT_TEMPLATE = 'reports/email/monitors/result.jinja'
    SPIDERMON_REPORT_CONTEXT = {
        'report_title': 'Spidermon File Report'
    }
    SPIDERMON_REPORT_FILENAME = 'my_report.html'

Settings available:

.. _SPIDERMON_REPORT_CONTEXT:

SPIDERMON_REPORT_CONTEXT
------------------------

Dictionary containing context variables to be included in your report.

.. _SPIDERMON_REPORT_FILENAME:

SPIDERMON_REPORT_FILENAME
-------------------------

String containing the path of the generated report file.

.. _SPIDERMON_REPORT_TEMPLATE:

SPIDERMON_REPORT_TEMPLATE
-------------------------

String containing the location of the template for the file report.

.. _actions-s3-report:

S3 Report action
================

This action works exactly like :ref:`actions-file-report` but instead of saving the
generated report locally, it uploads it to a S3 Amazon Bucket.

Settings available:

.. _SPIDERMON_REPORT_S3_BUCKET:

SPIDERMON_REPORT_S3_BUCKET
--------------------------

.. _SPIDERMON_REPORT_S3_CONTENT_TYPE:

SPIDERMON_REPORT_S3_CONTENT_TYPE
--------------------------------

.. _SPIDERMON_REPORT_S3_FILENAME:

SPIDERMON_REPORT_S3_FILENAME
----------------------------

.. _SPIDERMON_REPORT_S3_MAKE_PUBLIC:

SPIDERMON_REPORT_S3_MAKE_PUBLIC
-------------------------------

.. _SPIDERMON_REPORT_S3_REGION_ENDPOINT:

SPIDERMON_REPORT_S3_REGION_ENDPOINT
-----------------------------------

.. _actions-sentry-action:

Sentry action
============

This action allows you to send custom messages to `Sentry`_ when your
monitor suites finishes their execution. To use this action
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

The following settings are needed to make this action workable:

.. _SPIDERMON_SENTRY_DSN:

SPIDERMON_SENTRY_DSN
--------------------------

Data Source Name provided by `Sentry`_, it's a representation of the configuration required by the Sentry SDKs.

.. _SPIDERMON_SENTRY_PROJECT_NAME:

SPIDERMON_SENTRY_PROJECT_NAME
-------------------------------------

Project name to use in notification title.

.. _SPIDERMON_SENTRY_ENVIRONMENT_TYPE:

SPIDERMON_SENTRY_ENVIRONMENT_TYPE
-------------------------------------

Default: ``Development``

Environment type to use in notification title.
It could be set to anything like local, staging, development or production.

.. _SPIDERMON_SENTRY_LOG_LEVEL:

SPIDERMON_SENTRY_LOG_LEVEL
---------------------------

Default: ``error``

It could be set to any level provided by `Sentry Log Level`_

.. _SPIDERMON_SENTRY_FAKE:

SPIDERMON_SENTRY_FAKE
--------------------

Default: ``False``

If set `True`, the Sentry message will be in the logs but nothing will be sent.

.. _`Sentry`: https://sentry.io/
.. _`Sentry DSN`: https://docs.sentry.io/error-reporting/quickstart/?platform=python#configure-the-sdk
.. _`Sentry Log Level`: https://docs.sentry.io/enriching-error-data/context/?platform=python#setting-the-level

.. _actions-custom-action:

Custom actions
==============

You can define your own custom actions to be executed by your monitor suites. Just
create a class that inherits from `spidermon.core.actions.Action` and implement
the `run_action` method.

.. code-block:: python

    from spidermon.core.actions import Action

    class MyCustomAction(Action):
        def run_action(self):
            # Include here the logic of your action
            # (...)
