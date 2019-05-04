.. _slack_bot_guide:

==========================================
Guide to configure Slack bot for Spidermon
==========================================

Message to readers of this first draft.
Slack App's bot creating process is incredibly detailed. Hence, here's a simple guide to make that process easier for our users, focusing only on the details that are needed. Do try following the steps to setup Slack action from the start. To check if this clears it up.

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

**2. Creating a bot user**

To use your Slack App as a bot, first you'll need to create a `Bot User` for it.

Head to your app's settings page and click the `Bot Users` feature in the navigation menu.
You'll be presented with a button marked `Add a Bot` User, and when you click on it, you'll see a screen where you can configure your app's bot user with the following info:


- `Display name` - the name that is displayed to other users when the bot posts messages, or the bot's profile is viewed, etc.
- `Default username` - the string that is used when the bot is mentioned in a message. This username may be modified slightly from the default when it is installed to a workspace where that username is already reserved. This modification is an incrementing number appended to the username - so @username might become @username2.
- `Always Show My Bot as Online` - we recommend you enable this feature, so that your bot always appears to be online.

Once you've completed these fields, click the Add Bot User button and then Save Changes.

**3. Installing the bot to a workspace**
A bot user is added to a workspace by installing the app that the bot is associated with.

On your app's settings page again, click the Install App settings item in the navigation menu.

On this page, click a button marked `Install App` to your Workspace. If you had already installed your app, the button to click will instead be marked Reinstall App.
You'll see a permissions authorization page, where you should click `Authorize`.

Your app is now installed to that workspace, but you still need to invite it into individual channels.

Once installed, you will have generated a bot token that you should store for use later on - you can find it in your app's settings under Install App > Bot User OAuth Access Token. This `Bot User OAuth Access Token` is what we use for `SPIDERMON_SLACK_SENDER_TOKEN`.

Finishing up
============

1. **Adding Slack credentials to your Scrapy Project**

.. code-block:: python

    # settings.py
    SPIDERMON_SLACK_SENDER_TOKEN = 'YOUR_BOT_USER_OAUTH_ACCESS_TOKEN'
    SPIDERMON_SLACK_SENDER_NAME = 'YOUR_BOT_USERNAME'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']

Source of documentation: https://api.slack.com/bot-users
