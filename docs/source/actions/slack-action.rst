Slack action
============

This action allows you to send custom messages to a `Slack`_ channel (or user)
using a bot when your monitor suites finish their execution.

To use this action you need to:

#.  Install `slackclient`_ 2.0 or higher:

    .. code-block:: shell

        $ pip install "slackclient>=2.0"

#.  Provide the `Slack credentials`_ in your ``settings.py`` file as follows:

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = '<SLACK_SENDER_TOKEN>'
    SPIDERMON_SLACK_SENDER_NAME = '<SLACK_SENDER_NAME>'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']

A notification will look like the following one:

.. image:: /_static/slack_notification.png
   :scale: 50 %
   :alt: Slack Notification

Follow :ref:`these steps <configuring-slack-bot>` to configure your Slack bot.

The following settings are the minimum needed to make this action works:

SPIDERMON_SLACK_RECIPIENTS
--------------------------

List of recipients of the message. It could be a channel or an user.

SPIDERMON_SLACK_SENDER_NAME
---------------------------

Username of your bot.

SPIDERMON_SLACK_SENDER_TOKEN
----------------------------

`Bot User OAuth Access Token` of your bot.

.. warning::

    Be careful when using bot user tokens in Spidermon. Do not publish bot user tokens in public code repositories.

Other settings available:

SPIDERMON_SLACK_ATTACHMENTS
---------------------------

SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE
------------------------------------

SPIDERMON_SLACK_FAKE
--------------------

Default: ``False``

If set `True`, the Slack message content will be in the logs but nothing will be sent.

SPIDERMON_SLACK_INCLUDE_ATTACHMENTS
-----------------------------------

SPIDERMON_SLACK_INCLUDE_MESSAGE
-------------------------------

SPIDERMON_SLACK_MESSAGE
-----------------------

SPIDERMON_SLACK_MESSAGE_TEMPLATE
--------------------------------

SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS
--------------------------------------------------

SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS
-----------------------------------------------

SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK
--------------------------------------------

SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX
-------------------------------------

.. _`Slack`: https://slack.com/
.. _`Slack credentials`: https://api.slack.com/docs/token-types
.. _`slackclient`: https://pypi.org/project/slackclient/
