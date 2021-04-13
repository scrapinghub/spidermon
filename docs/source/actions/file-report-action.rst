File Report Action
==================

This action allows to create a file report based on a template. You can
use `Jinja2`_ as your template engine.

In this example we will create a file called `my_report.html` when the monitor suite finishes:

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.reports.files import CreateFileReport

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_finished_actions = [
            CreateFileReport,
        ]

.. code-block:: python

    # settings.py
    SPIDERMON_REPORT_TEMPLATE = 'reports/email/monitors/result.jinja'
    SPIDERMON_REPORT_CONTEXT = {
        'report_title': 'Spidermon File Report'
    }
    SPIDERMON_REPORT_FILENAME = 'my_report.html'

Settings available:

SPIDERMON_REPORT_CONTEXT
------------------------

Dictionary containing context variables to be included in your report.

SPIDERMON_REPORT_FILENAME
-------------------------

String containing the path of the generated report file.

SPIDERMON_REPORT_TEMPLATE
-------------------------

String containing the location of the template for the file report.

S3 Report action
================

This action works exactly like `File Report Action`_ but instead of saving the
generated report locally, it uploads it to a S3 Amazon Bucket.

Settings available:

SPIDERMON_REPORT_S3_BUCKET
--------------------------

SPIDERMON_REPORT_S3_CONTENT_TYPE
--------------------------------

SPIDERMON_REPORT_S3_FILENAME
----------------------------

SPIDERMON_REPORT_S3_MAKE_PUBLIC
-------------------------------

SPIDERMON_REPORT_S3_REGION_ENDPOINT
-----------------------------------

.. _Jinja2: http://jinja.pocoo.org/
