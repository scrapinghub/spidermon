.. _slack_bot_guide:

==========================================
Guide to configure Slack bot for Spidermon
==========================================

What are bots?
==============

A bot is a type of Slack App designed to interact with users via conversation.

To work with Slack Actions, you will need a Slack bot which would send notification to your Slack workplace from Spidermon.

Getting Started
===============

.. note:
    You would need to be leader of Slack workplace for which you are trying to create a bot.

**1. Create a Slack App**
Start here --> https://api.slack.com/apps?new_app=1

- `App Name` - the name of your Slack app displayed to other users when Slack app profile is viewed.
- `Development Slack Workspace` - the workplace where Spidermon will send its notifications.

**2. Create a bot user**

To use your Slack App as a bot, you'll need to create a `Bot User` for it. Once the bot user is added and
changes are saved, copy the username as we would need this in the last step.

**3. Installing the bot to a workspace**
A bot user is added to a workspace by installing the app that the bot is associated with.
Hence, install your newly created app to your workspace and authorize if prompted for permissions.

Once installed, you can find Bot User OAuth Access Token in the settings. This `Bot User OAuth Access Token` is what we use for `SPIDERMON_SLACK_SENDER_TOKEN`.

Finishing up
============

1. **Adding Slack credentials to your Scrapy Project**

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = 'YOUR_BOT_USER_OAUTH_ACCESS_TOKEN'
    SPIDERMON_SLACK_SENDER_NAME = 'YOUR_BOT_USERNAME'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']

Source of documentation: https://api.slack.com/bot-users
