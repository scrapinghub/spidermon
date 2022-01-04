.. _configuring-slack-bot:

How do I configure a Slack bot for Spidermon?
=============================================

What are bots?
--------------

A bot is a type of Slack App designed to interact with users via conversation.

To work with :doc:`Slack Actions </actions/slack-action>`, you will need a Slack bot which would
send notifications to your Slack workspace from Spidermon.

Steps
-----

.. note:
    You need to be the `owner/admin <https://get.slack.help/hc/en-us/articles/201314026-Understanding-roles-permissions-inside-Slack>`_ of the `Slack workspace <https://get.slack.help/hc/en-us/articles/206845317-Create-a-Slack-workspace>`_ for which you are trying to create a bot.

#. `Create a Slack bot app <https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace>`_.

#. Go to the `OAuth & Permissions` tab on the left sidebar.

#. Under `Bot Token Scopes` make sure the bot has the ``chat:write`` permission.

#. Once the bot is installed to your workspace, copy the Bot User OAuth Access Token from this tab. This `Bot User OAuth Access Token` is what we use for ``SPIDERMON_SLACK_SENDER_TOKEN``.

#. Lastly, add your Slack credentials to your Scrapy project's settings.

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = 'YOUR_BOT_USER_OAUTH_ACCESS_TOKEN'
    SPIDERMON_SLACK_SENDER_NAME = 'YOUR_BOT_USERNAME'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']
