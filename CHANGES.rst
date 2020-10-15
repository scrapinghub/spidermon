Release notes
=============

1.14.0 (2020-10-05)
-------------------
- feature: Built-in monitor for field and item coverage (`issue#253 <https://github.com/scrapinghub/spidermon/issues/253>`_)
- feature: Add field coverage statistics (`PR#262 <https://github.com/scrapinghub/spidermon/pull/262>`_)
- chore: Update required slackclient version (`PR#265 <https://github.com/scrapinghub/spidermon/pull/265>`_)
- chore: Add Python 3.8 support (`issue#255 <https://github.com/scrapinghub/spidermon/issues/255>`_)
- chore: Drop Python 3.5 support (`issue#266 <https://github.com/scrapinghub/spidermon/issues/266>`_)
- chore: Remove test decorator that skips tests if executed in old Python versions (`PR#258 <https://github.com/scrapinghub/spidermon/pull/258>`_)
- chore: Fix deprecation warnings (`PR#272 <https://github.com/scrapinghub/spidermon/pull/272>`_, `PR#274 <https://github.com/scrapinghub/spidermon/pull/274>`_)
- docs: Fix inconsistent examples (`PR#273 <https://github.com/scrapinghub/spidermon/pull/273>`_)

1.13.0 (2020-06-23)
-------------------
- bug: Fix Telegram action error logging
- feature: Disable item validation pipeline when Spidermon is disabled
- feature: Item validation built in monitor
- chore: Removed Python 2.7 support
- docs: Improved documentation organization

1.12.2 (2020-05-07)
-------------------
- Fixed version 1.12.1 changelog

1.12.1 (2020-05-07)
-------------------
- bugfix: AttributeError when using ValidationMonitorMixin (`issue <https://github.com/scrapinghub/spidermon/issues/246>`_)
- docs: How-To Guide - Adding required fields coverage validation (`pull request <https://github.com/scrapinghub/spidermon/pull/247>`_)

1.12.0 (2020-01-09)
-------------------

- Dropped python 3.4 support
- Added action to send monitor reports to Telegram
- Added fallback to scrapy AWS settings
- Logged errors from Slack API calls
- Allowed to define SPIDERMON_SLACK_RECIPIENTS setting as a comma-separated string with the desired recipients
- Read SES settings with getlist
- Added documentation of Expression Monitors
- Improved Slack action documentation
- Fixed sphinx warnings when building docs
- Fixed warnings in docs build
- Validate docs build in CI
- Applied and enforced black formatting on spidermon source code
- Configured test coverage reporting in project

1.11.0 (2019-08-02)
-------------------

- Allowed per-field checking in ValidationMonitorMixin
- Added option to set AWS Region Name on SES E-Mail action
- Added default value for 'SPIDERMON_BODY_HTML_TEMPLATE' setting
- Fixed bug in logging of Slack messages when fake setting is enabled
- Enforced lxml 4.3.5 or lower for Python 3.4
- Improved stats history documentation

1.10.2 (2019-07-01)
-------------------

- Version 1.10.1 with CHANGELOG updated

1.10.1 (2019-07-01)
-------------------

- Allowed to add absolute location for custom templates

1.10.0 (2019-06-12)
-------------------

- Added new StatsCollector that access stats data from previous spider executions.
- Added new setting to define the max number of unwanted HTTP status codes allowed in built-in monitor.
- Improved validation error messages with JSON Schema when additional fields are found.
- Made possible to retrieve JSON schema files from external locations.
- Included documentation of periodic monitor suites.
- Fixed bug caused by new slackclient release.
- Other small documentation improvements.

1.9.0 (2019-03-11)
------------------

- Add set of built-in basic monitors with the most common test methods to allow
  start monitoring spiders more straightforward.
- Add SendSentryMessage action to send notifications to Sentry containing the
  results of Spidermon execution.
- Add SPIDERMON_ENGINE_STOP_MONITORS setting to list monitors to be executed
  when the Scrapy engine is stopped.
- Fix bug that prevented the use of custom model-level validators in schematics models.
- Refactor JSONSchemaValidator to allow select different versions of JSON Schema.
- Refactor requirements in setup.py to include missing required dependencies.
- Fix bug caused by backward incompatible change in jsonschema 3.0.0.
- Fix example code of tutorial.
- Install documentation improvements.

1.8.0 (2019-01-08)
------------------

- Remove CreateJobReport action.
- Include new documentation and tutorial code.
- Rename internal method in MonitorRunner to fix typo.

1.7.0 (2018-12-04)
------------------

- Support universal wheels.
- Skip authentication and recipient settings when running in fake mode.

1.6.0 (2018-11-09)
------------------

- Add SPIDERMON_EMAIL_CONTEXT setting to pass custom contexts to email actions.
- Add support for Schematics 2.1.0.

1.5.0 (2018-09-19)
------------------

- Convert the job ID tag into a clickable button.

1.4.0 (2018-08-17)
------------------

- Avoid requests to get the amount of lines in the log by default, because
  they consume too much memory and they are very slow. You can still use
  the old behavior adding ``show_log_count`` to the context before creating
  the email message.
- Refactor the requirements in setup.py.
- Update the Sphinx configuration.

1.3.0 (2018-08-02)
------------------

- Add support for periodic monitors in the Scrapy extension.

1.2.0 (2018-04-04)
------------------

- Modify ItemValidationPipeline in order to support dict objects in addition
  to Scrapy.Item objects.
- Refactor ItemValidationPipeline to make it easier to extend this class.

1.1.0 (2018-03-23)
------------------

- Add Schematics 2.* support. Note that Schematics 2.0.0 introduced many
  changes to its API and even some validation rules have a slightly different
  behaviour in some cases.
- ItemValidationPipeline optimisations for cases where no validators can be
  applied.

1.0.0 (2018-03-08)
------------------

- Add Python 3 support.
- Run tests on Python 2 and Python 3.
- Add dependencies for optional validation features to setup.py.
- Import HubstorageClient from the scrapinghub library if available.
- Replace dash.scrapinghub.com with app.scrapinghub.com.

Backwards Incompatible Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Rename attachements attribute in the SendSlackMessage class to attachments.
- Add the SPIDERMON_ENABLED setting to control if the Scrapy extension should
  run (note that it is disabled by default).
