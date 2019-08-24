.. _steps:

==========================================
Guide to configure Slack bot for Spidermon
==========================================

What are bots?
==============

A bot is a type of Slack App designed to interact with users via conversation.

To work with Slack Actions, you will need a Slack bot which would send notification to your Slack workplace from Spidermon.

Steps
=====

.. note:
    You would need to be leader of Slack workplace for which you are trying to create a bot.

1. `Create a Slack bot <https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace>`_ by following the steps listed here.

2. Once bot is installed, you can find Bot User OAuth Access Token in the settings. This `Bot User OAuth Access Token` is what we use for `SPIDERMON_SLACK_SENDER_TOKEN`.

3. Adding Slack credentials to your Scrapy Project

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = 'YOUR_BOT_USER_OAUTH_ACCESS_TOKEN'
    SPIDERMON_SLACK_SENDER_NAME = 'YOUR_BOT_USERNAME'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']
