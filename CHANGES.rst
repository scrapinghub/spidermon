Release notes
=============

1.19.0 (2023-07-07)
-------------------

- bug: Fix ``JobTagsAction`` failing due to ``JobMetadata`` not longer supporting ``__setitem__`` method (`PR#404 <https://github.com/scrapinghub/spidermon/pull/404>`_)
- feature: Add ``PeriodicItemCountMonitor`` to check for increase in item count. Also included ``PeriodicItemCountMonitorSuite`` suite (`PR#402 <https://github.com/scrapinghub/spidermon/pull/402>`_)
- chore: Deprecate  support for data validation using ``schematics`` (`PR#399 <https://github.com/scrapinghub/spidermon/pull/399>`_)
- chore: Drop support for Python 3.6 and Python 3.7. Added support for Python 3.11 (`PR#398 <https://github.com/scrapinghub/spidermon/pull/398>`_)
- feature: Add ability to pass kwargs to Slack APIs (`PR#397 <https://github.com/scrapinghub/spidermon/pull/397>`_)

1.18.0 (2023-03-13)
-------------------

- feature: Support setting the ``Return-Path`` for Amazon SES emails (`PR#381 <https://github.com/scrapinghub/spidermon/pull/381>`_)
- bug: Fix ``BaseStatMonitor`` failing in Scrapy Cloud when settings were provided as strings (`PR#378 <https://github.com/scrapinghub/spidermon/pull/378>`_)
- feature: Add setting ``SPIDERMON_FIELD_COVERAGE_SKIP_IF_NO_ITEM`` to allow skipping ``FieldCoverageMonitor`` if no items were scraped (`PR#372 <https://github.com/scrapinghub/spidermon/pull/372>`_)
- feature: Add ``Fallback Actions``. ``Action`` now allows to define ``fallback`` field that may contain an additional ``Action`` to be executed if an exception is raised during the main action (`PR#365 <https://github.com/scrapinghub/spidermon/pull/365>`_)
- feature: Use ``ItemAdapter`` when working with items to support the same types of item as Scrapy (`PR#358 <https://github.com/scrapinghub/spidermon/pull/358>`_)
- chore: Refactor code from ``spider.contrib.scrapy`` into ``base``, ``monitors`` and ``suites`` subpackages (`PR#386 <https://github.com/scrapinghub/spidermon/pull/386>`_)
- chore: Replace ``tox pep8`` functionality with ``pre-commit`` git hooks (`PR#387 <https://github.com/scrapinghub/spidermon/pull/387>`_)
- chore: Update contributing guidelines to include reference to ``pre-commit`` tool (`PR#392 <https://github.com/scrapinghub/spidermon/pull/392>`_)

1.17.1 (2023-01-05)
-------------------

- bug: Fix Slack dependency name issue (`PR#367 <https://github.com/scrapinghub/spidermon/pull/367>`_)
- chore: Change the Ubuntu version on workflow settings (`PR#373 <https://github.com/scrapinghub/spidermon/pull/373>`_)
- docs: Adding PeriodicExecutionTimeMonitor to the batteries docs (`PR#368 <https://github.com/scrapinghub/spidermon/pull/368>`_)
- feature: Adding the use of ItemAdapter to prevent assumptions of item nature (`PR#358 <https://github.com/scrapinghub/spidermon/pull/358>`_)
- misc: Fix compatibility issues with jsonschema>=4 (`PR#364 <https://github.com/scrapinghub/spidermon/pull/364>`_)

1.17.0 (2022-09-12)
-------------------

- feature: Updated `DownloaderExceptionMonitor` and `ItemValidationMonitor` to inherit from `BaseStatMonitor` (`PR#334 <https://github.com/scrapinghub/spidermon/pull/334>`_, `PR#335 <https://github.com/scrapinghub/spidermon/pull/335>`_)
- feature: Updated Slack action to use `slack-sdk <https://pypi.org/project/slack-sdk/>`_ as library in replacement of deprecated `slackclient <https://pypi.org/project/slackclient/>`_ (`PR#313 <https://github.com/scrapinghub/spidermon/issues/313>`_)
- feature: Added new action to allow to send notification to Discord channels (`PR#348 <https://github.com/scrapinghub/spidermon/pull/348>`_)
- feature: Added Python 3.10 support (`PR#349 <https://github.com/scrapinghub/spidermon/pull/349>`_)
- feature: Added new action to allow to send email notifications using SMTP server (`PR#345 <https://github.com/scrapinghub/spidermon/pull/345>`_)
- misc: small bug fixes and documentation improvements that can be checked in the `milestone summary <https://github.com/scrapinghub/spidermon/milestone/13?closed=1>`_.

1.16.2 (2021-12-23)
-------------------
- feature: Create base class to aid the creation of custom monitors that only validates against a job stat value (`PR#325 <https://github.com/scrapinghub/spidermon/pull/325>`_)
- feature: Add built-in monitor for critical errors (`PR#329 <https://github.com/scrapinghub/spidermon/pull/329>`_)
- feature: Use new base class to implement some built-in monitors (`PR#326 <https://github.com/scrapinghub/spidermon/pull/326>`_ `PR#327 <https://github.com/scrapinghub/spidermon/pull/327>`_ `PR#328 <https://github.com/scrapinghub/spidermon/pull/328>`_)
- feature: Add new built-in monitors for common validations (`PR#284 <https://github.com/scrapinghub/spidermon/pull/284>`_)
- bug: Allow Slack bot to send notification correctly even if an icon URL is not defined to the bot (`PR#307 <https://github.com/scrapinghub/spidermon/pull/307>`_)
- bug: Fix regex to match validation error message from schematics library (`PR#310 <https://github.com/scrapinghub/spidermon/pull/310>`_)
- chore: Remove six library and upgrade Python syntax (`PR#270 <https://github.com/scrapinghub/spidermon/pull/270>`_)
- chore: Remove travis and configure Github Actions (`PR#291 <https://github.com/scrapinghub/spidermon/pull/291>`_)

1.15.2 (2021-10-04)
-------------------
- chore: Add Github Actions support and remove Travis

1.15.1 (2021-10-04)
-------------------
- chore: Pin `jsonschema` version to 3.2.0 to avoid problems with newest version that has backward incompatible changes
- chore: Pin `schematics` version to 2.1.0 to avoid problems with newest version that has backward incompatible changes

1.15.0 (2021-04-06)
-------------------
- feature: Improve content of Sentry messages (`PR#279 <https://github.com/scrapinghub/spidermon/pull/279>`_)
- bug: Replace `boto` with `boto3` for Amazon SES work correctly (`issue#285 <https://github.com/scrapinghub/spidermon/issues/285>`_)

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
