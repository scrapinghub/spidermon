.. _topics-settings:

========
Settings
========

The Spidermon settings allows you to customize the behaviour of your monitors
enabling, disabling and configuring features like enabled monitors, monitor
actions, item validation and notifications.

.. _topics-settings-ref:

Built-in settings reference
===========================

Here's a list of all available Spidermons settings, in alphabetical order, along
with their default values and the scope where they apply. These settings must
be defined in `settings.py` file of your Scrapy project.

.. setting:: SPIDERMON_AWS_ACCESS_KEY

SPIDERMON_AWS_ACCESS_KEY
------------------------

.. setting:: SPIDERMON_AWS_SECRET_KEY

SPIDERMON_AWS_SECRET_KEY
------------------------

.. setting:: SPIDERMON_ENABLED

SPIDERMON_ENABLED
-----------------

Default: ``False``

Whether to enable Spidermon.

.. setting:: SPIDERMON_EXPRESSIONS_MONITOR_CLASS

SPIDERMON_EXPRESSIONS_MONITOR_CLASS
-----------------------------------

.. setting:: SPIDERMON_PERIODIC_MONITORS

SPIDERMON_PERIODIC_MONITORS
---------------------------

.. setting:: SPIDERMON_SPIDER_CLOSE_MONITORS

SPIDERMON_SPIDER_CLOSE_MONITORS
-------------------------------

.. setting:: SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS

SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS
------------------------------------------

.. setting:: SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS

SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS
-----------------------------------------

.. setting:: SPIDERMON_SPIDER_OPEN_MONITORS

SPIDERMON_SPIDER_OPEN_MONITORS
------------------------------

.. _topics-settings-email-action-ref:

E-mail action settings reference
================================

.. setting:: SPIDERMON_BODY_HTML

SPIDERMON_BODY_HTML
-------------------

.. setting:: SPIDERMON_BODY_HTML_TEMPLATE

SPIDERMON_BODY_HTML_TEMPLATE
----------------------------

.. setting:: SPIDERMON_BODY_TEXT

SPIDERMON_BODY_TEXT
-------------------

.. setting:: SPIDERMON_BODY_TEXT_TEMPLATE

SPIDERMON_BODY_TEXT_TEMPLATE
----------------------------

.. setting:: SPIDERMON_EMAIL_BCC

SPIDERMON_EMAIL_BCC
-------------------

.. setting:: SPIDERMON_EMAIL_CC

SPIDERMON_EMAIL_CC
------------------

.. setting:: SPIDERMON_EMAIL_FAKE

SPIDERMON_EMAIL_FAKE
--------------------

.. setting:: SPIDERMON_EMAIL_REPLY_TO

SPIDERMON_EMAIL_REPLY_TO
------------------------

.. setting:: SPIDERMON_EMAIL_SENDER

SPIDERMON_EMAIL_SENDER
----------------------

.. setting:: SPIDERMON_EMAIL_SUBJECT

SPIDERMON_EMAIL_SUBJECT
-----------------------

.. setting:: SPIDERMON_EMAIL_SUBJECT_TEMPLATE

SPIDERMON_EMAIL_SUBJECT_TEMPLATE
--------------------------------

.. setting:: SPIDERMON_EMAIL_TO

SPIDERMON_EMAIL_TO
------------------

.. _topics-settings-slack-action-ref:

Slack action settings reference
===============================

.. setting:: SPIDERMON_SLACK_ATTACHMENTS

SPIDERMON_SLACK_ATTACHMENTS
---------------------------

.. setting:: SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE

SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE
------------------------------------

.. setting:: SPIDERMON_SLACK_FAKE

SPIDERMON_SLACK_FAKE
--------------------

.. setting:: SPIDERMON_SLACK_INCLUDE_ATTACHMENTS

SPIDERMON_SLACK_INCLUDE_ATTACHMENTS
-----------------------------------

.. setting:: SPIDERMON_SLACK_INCLUDE_MESSAGE

SPIDERMON_SLACK_INCLUDE_MESSAGE
-------------------------------

.. setting:: SPIDERMON_SLACK_MESSAGE

SPIDERMON_SLACK_MESSAGE
-----------------------

.. setting:: SPIDERMON_SLACK_MESSAGE_TEMPLATE

SPIDERMON_SLACK_MESSAGE_TEMPLATE
--------------------------------

.. setting:: SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS

SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS
--------------------------------------------------

.. setting:: SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS

SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS
-----------------------------------------------

.. setting:: SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK

SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK
--------------------------------------------

.. setting:: SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX

SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX
-------------------------------------

.. setting:: SPIDERMON_SLACK_RECIPIENTS

SPIDERMON_SLACK_RECIPIENTS
--------------------------

.. setting:: SPIDERMON_SLACK_SENDER_NAME

SPIDERMON_SLACK_SENDER_NAME
---------------------------

.. setting:: SPIDERMON_SLACK_SENDER_TOKEN

SPIDERMON_SLACK_SENDER_TOKEN
----------------------------

.. _topics-settings-report-action-ref:

Report action settings reference
=========================

.. setting:: SPIDERMON_JOBREPORT_APIKEY

SPIDERMON_JOBREPORT_APIKEY
--------------------------

.. setting:: SPIDERMON_JOBREPORT_CONTENTTYPE

SPIDERMON_JOBREPORT_CONTENTTYPE
-------------------------------

.. setting:: SPIDERMON_JOBREPORT_KEY

SPIDERMON_JOBREPORT_KEY
-----------------------

.. setting:: SPIDERMON_JOB_TAGS_TO_ADD

SPIDERMON_JOB_TAGS_TO_ADD
-------------------------

.. setting:: SPIDERMON_JOB_TAGS_TO_REMOVE

SPIDERMON_JOB_TAGS_TO_REMOVE
----------------------------

.. _topics-settings-s3-report-ref:

S3 Report settings reference
============================

.. setting:: SPIDERMON_REPORT_CONTEXT

SPIDERMON_REPORT_CONTEXT
------------------------

.. setting:: SPIDERMON_REPORT_FILENAME

SPIDERMON_REPORT_FILENAME
-------------------------

.. setting:: SPIDERMON_REPORT_S3_BUCKET

SPIDERMON_REPORT_S3_BUCKET
--------------------------

.. setting:: SPIDERMON_REPORT_S3_CONTENT_TYPE

SPIDERMON_REPORT_S3_CONTENT_TYPE
--------------------------------

.. setting:: SPIDERMON_REPORT_S3_FILENAME

SPIDERMON_REPORT_S3_FILENAME
----------------------------

.. setting:: SPIDERMON_REPORT_S3_MAKE_PUBLIC

SPIDERMON_REPORT_S3_MAKE_PUBLIC
-------------------------------

.. setting:: SPIDERMON_REPORT_S3_REGION_ENDPOINT

SPIDERMON_REPORT_S3_REGION_ENDPOINT
-----------------------------------

.. setting:: SPIDERMON_REPORT_TEMPLATE

SPIDERMON_REPORT_TEMPLATE
-------------------------

.. _topics-settings-item-validation-ref:

Item validation settings reference
==================================

.. setting:: SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS

SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS
----------------------------------------

.. setting:: SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS

SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS
-------------------------------------------

.. setting:: SPIDERMON_VALIDATION_ERRORS_FIELD

SPIDERMON_VALIDATION_ERRORS_FIELD
---------------------------------

.. setting:: SPIDERMON_VALIDATION_MODELS

SPIDERMON_VALIDATION_MODELS
---------------------------

.. setting:: SPIDERMON_VALIDATION_SCHEMAS

SPIDERMON_VALIDATION_SCHEMAS
----------------------------
