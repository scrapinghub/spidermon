.. _configuring-telegram-bot:

======================================
Configure a Telegram bot for Spidermon
======================================

What are bots?
==============

A bot is a type of Telegram user designed to interact with users via conversation.

To work with `Telegram Actions <https://spidermon.readthedocs.io/en/latest/actions.html#telegram-action>`_, you will need a Telegram bot which would send `notifications <https://spidermon.readthedocs.io/en/latest/getting-started.html#telegram-notifications>`_ to Telegram from Spidermon.

Steps
=====

1. `Create a Telegram bot <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_.

2. Once your bot is created, you will receive its Authorization Token. This `Bot Authorization Token` is what we use for ``SPIDERMON_TELEGRAM_SENDER_TOKEN``.

3. Add your Telegram bot credentials to your Scrapy project's settings.

4. Add the recipients to your Scrapy project's settings, getting the `chat_id` or `group_id` is not straightforward, there is an info bot that can help with this. Just forward a message from the user or group that you want to receive Spidermon notifications to `[@GroupIDbot](https://t.me/GroupIDbot)` and it will reply with the id. To forward a message from a group to the bot, you need to add the bot to that group before.

5. For notifications in groups: `Add your self-created bot <https://telegram.org/faq#q-how-do-i-add-more-members-what-39s-an-invite-link>`_ (from step 1.) to your group.
For notifictations in channels: Add your self-created bot (from step 1.) as administrator to your channel (not possible in browser version).


.. note:
    You need to add the bot to the group or channel so it can send messages. If you want the bot to send notifications to a user, first the user needs to start a conversation with the bot and send the command `/start`.

.. code-block:: python

    # settings.py
    SPIDERMON_TELEGRAM_SENDER_TOKEN = 'YOUR_BOT_AUTHORIZATION_TOKEN'
    SPIDERMON_TELEGRAM_RECIPIENTS = ['chat_id', 'group_id', '@channelname']
