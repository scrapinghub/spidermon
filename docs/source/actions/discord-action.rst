Discord action
===============

This action allows you to send custom messages to a `Discord`_ channel
using a bot when your monitor suites finish their execution.

To use this action you need to provide the `Discord webhook url`_ in your ``settings.py`` file as follows:

.. code-block:: python

    # settings.py
    SPIDERMON_DISCORD_WEBHOOK_URL = '<DISCORD_WEBHOOK_URL>'

A notification will look like the following:

.. image:: /_static/discord_notification.png
   :scale: 50 %
   :alt: Discord Notification

Follow :ref:`these steps <configuring-discord-bot>` to configure your Discord bot.

The following settings are the minimum needed to make this action work:

SPIDERMON_DISCORD_WEBHOOK_URL
-------------------------------

`Webhook URL` of your bot.

.. warning::

    Be careful when using bot webhooks url in Spidermon. Do not publish them in public code repositories.

Other settings available:

.. _SPIDERMON_DISCORD_FAKE:

_SPIDERMON_DISCORD_FAKE
-----------------------

Default: ``False``

If set `True`, the Discord message content will be in the logs but nothing will be sent.

.. _SPIDERMON_DISCORD_MESSAGE:

SPIDERMON_DISCORD_MESSAGE
--------------------------

The message to be sent, it supports Jinja2 template formatting.

.. _SPIDERMON_DISCORD_MESSAGE_TEMPLATE:

SPIDERMON_DISCORD_MESSAGE_TEMPLATE
-----------------------------------

Path to a Jinja2 template file to format messages sent by the Discord Action.

.. _`Discord`: https://discord.com/
.. _`Discord webhook url`: https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
