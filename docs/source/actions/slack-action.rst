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
    SPIDERMON_SLACK_SENDER_TOKEN = "<SLACK_SENDER_TOKEN>"
    SPIDERMON_SLACK_SENDER_NAME = "<SLACK_SENDER_NAME>"
    SPIDERMON_SLACK_RECIPIENTS = ["@yourself", "#yourprojectchannel"]

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

Default ``None``

A string representing a `slack message attachment`_ JSON block.

SPIDERMON_SLACK_ATTACHMENTS_TEMPLATE
------------------------------------

Default ``None``

Absolute path to a `Jinja2`_ template from which slack messages will be constructed from.
If None it will use the default template from `the notifier templates folder <https://github.com/scrapinghub/spidermon/tree/master/spidermon/contrib/actions/slack/templates/slack/spider/notifier>`_.

SPIDERMON_SLACK_FAKE
--------------------

Default: ``False``

If set `True`, the Slack message content will be in the logs but nothing will be sent.

SPIDERMON_SLACK_INCLUDE_ATTACHMENTS
-----------------------------------

Default ``True``

Include attachment content in slack notification.

SPIDERMON_SLACK_INCLUDE_MESSAGE
-------------------------------

Default ``True``

Include message content in slack notification.

SPIDERMON_SLACK_MESSAGE
-----------------------

Default ``None``

A string representing containing standard text to send as a slack message.

SPIDERMON_SLACK_MESSAGE_TEMPLATE
--------------------------------

Default: ``None``

Absolute path to a `Jinja2`_ template from which slack messages will be constructed from.
If None it will use the default template from the `notifier templates folder`_.


SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS
--------------------------------------------------

Default: ``True``

For `SendSlackMessageSpiderFinished` notifier only. Whether to include attachments in error notification messages.

SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS
-----------------------------------------------

Default: ``False``

For `SendSlackMessageSpiderFinished` notifier only. Whether to include attachments in ok notification messages.

SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK
--------------------------------------------

Default: ``False``

For `SendSlackMessageSpiderFinished` notifier only. Whether to include a link to a spidermon report. See `file report actions`_.

SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX
-------------------------------------

Default: ``0``

For `SendSlackMessageSpiderFinished` notifier only. The index of the report to link if multiple reports generated. See `file report actions`_.

.. _`Slack`: https://slack.com/
.. _`Slack credentials`: https://api.slack.com/docs/token-types
.. _`slackclient`: https://pypi.org/project/slackclient/
.. _`slack message attachment`: https://api.slack.com/reference/messaging/attachments
.. _`Jinja2`: http://jinja.pocoo.org/
.. _`notifier templates folder`: https://github.com/scrapinghub/spidermon/tree/master/spidermon/contrib/actions/slack/templates/slack/spider/notifier
.. _`file report actions`: https://spidermon.readthedocs.io/en/latest/actions/file-report-action.html
