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

.. _custom-templates:

Custom templates
-----------------

Actions that render a report or message from a `Jinja2`_ template (the
``*_TEMPLATE`` settings described on the following pages) accept an absolute
path to your own template file.

Templates receive ``result``, ``data``, ``monitors_passed`` and
``monitors_failed`` in their context, plus any variables you pass through the
action's own ``*_CONTEXT`` setting (e.g. ``SPIDERMON_EMAIL_CONTEXT``).

To tweak part of a built-in template instead of replacing it, extend it and
override one of its blocks. For example, to add a note above the default
email/file report:

.. code-block:: jinja

    {% extends "reports/email/monitors/result.jinja" %}
    {% block page_content %}
        <p>Custom note.</p>
        {{ super() }}
    {% endblock %}

.. _Jinja2: https://jinja.palletsprojects.com/en/stable/
