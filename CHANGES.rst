Release notes
=============

1.2.0 (TBD)
------------------

- Modify ItemValidationPipeline in order to support dict objects in addition
  to Scrapy.Item objects.

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
