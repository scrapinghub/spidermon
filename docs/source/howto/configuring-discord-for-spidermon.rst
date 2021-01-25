.. _configuring-discord-bot:

How do I configure a Discord bot for Spidermon?
================================================

What are bots?
--------------

A bot is a type of Discord user designed to interact with users via conversation.

To work with `Discord Actions <https://spidermon.readthedocs.io/en/latest/actions.html#discord-action>`_,
you will need a Discord webhook which would send `notifications <https://spidermon.readthedocs.io/en/latest/getting-started.html#discord-notifications>`_
to Discord from Spidermon.

Steps
-----

#. `Create a Discord webhook <https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks>`_.

#. Once your webhook is created, you will receive its URL. This is what we use for ``SPIDERMON_DISCORD_WEBHOOK_URL``.

#. Add your Discord bot credential to your Scrapy project's settings. That's it.

.. code-block:: python

    # settings.py
    SPIDERMON_DISCORD_WEBHOOK_URL = 'DISCORD_WEBHOOK_URL'
