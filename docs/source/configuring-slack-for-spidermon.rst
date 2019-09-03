.. _configuring-slack-bot:

====================================
Configure a Slack bot for Spidermon
====================================

What are bots?
==============

A bot is a type of Slack App designed to interact with users via conversation.

To work with `Slack Actions <https://spidermon.readthedocs.io/en/latest/actions.html#slack-action>`_, you will need a Slack bot which would send `notifications <https://spidermon.readthedocs.io/en/latest/getting-started.html#slack-notifications>`_ to your Slack workspace from Spidermon.

Steps
=====

.. note:
    You need to be the `owner/admin <https://get.slack.help/hc/en-us/articles/201314026-Understanding-roles-permissions-inside-Slack>`_ of the `Slack workspace <https://get.slack.help/hc/en-us/articles/206845317-Create-a-Slack-workspace>`_ for which you are trying to create a bot.

1. `Create a Slack bot <https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace>`_.

2. Once your bot is created, you can find Bot User OAuth Access Token in its settings. This `Bot User OAuth Access Token` is what we use for ``SPIDERMON_SLACK_SENDER_TOKEN``.

3. Lastly, add your Slack credentials to your Scrapy project's settings.

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = 'YOUR_BOT_USER_OAUTH_ACCESS_TOKEN'
    SPIDERMON_SLACK_SENDER_NAME = 'YOUR_BOT_USERNAME'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']
