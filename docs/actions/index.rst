Actions
=======

By default, when a monitor suite finishes, the pass/fail information is included
in the spider logs, which would be enough during development but useless when
you are monitoring several spiders.

Spidermon allows you to define actions that are ran after the monitors finish.
You can define your own actions or use one of the existing built-in actions.

.. toctree::
   :maxdepth: 1

   email-action
   slack-action
   telegram-action
   discord-action
   job-tags-action
   file-report-action
   sentry-action
   sns-action
   custom-action
