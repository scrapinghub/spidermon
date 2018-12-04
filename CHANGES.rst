Release notes
=============

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
