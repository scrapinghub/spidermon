Telegram action
===============

This action allows you to send custom messages to a `Telegram`_ channel, group or user
using a bot when your monitor suites finish their execution.

To use this action you need to provide the `Telegram bot token`_ in your ``settings.py`` file as follows:

.. code-block:: python

    # settings.py
    SPIDERMON_TELEGRAM_SENDER_TOKEN = '<TELEGRAM_SENDER_TOKEN>'
    SPIDERMON_TELEGRAM_RECIPIENTS = ['chatid', 'groupid' '@channelname']

A notification will look like the following:

.. image:: /_static/telegram_notification.png
   :scale: 50 %
   :alt: Telegram Notification

Follow :ref:`these steps <configuring-telegram-bot>` to configure your Telegram bot.

The following settings are the minimum needed to make this action work:

SPIDERMON_TELEGRAM_RECIPIENTS
-----------------------------

List of recipients of the message. It could be a user id, group id or channel name.

SPIDERMON_TELEGRAM_SENDER_TOKEN
-------------------------------

`Bot Authorization Token` of your bot.

.. warning::

    Be careful when using bot user tokens in Spidermon. Do not publish bot user tokens in public code repositories.

Other settings available:

SPIDERMON_TELEGRAM_FAKE
-----------------------

Default: ``False``

If set `True`, the Telegram message content will be in the logs but nothing will be sent.

SPIDERMON_TELEGRAM_MESSAGE
--------------------------

The message to be sent, it supports Jinja2 template formatting.

SPIDERMON_TELEGRAM_MESSAGE_TEMPLATE
-----------------------------------

Path to a Jinja2 template file to format messages sent by the Telegram Action.

.. _`Telegram`: https://telegram.org/
.. _`Telegram bot token`: https://core.telegram.org/bots
