Job tags action
===============

If you are running your spider using the `Scrapy Cloud`_ you are able to include
tags in your jobs. Spidermon includes two actions that may be used to add or to
remove tags to your jobs depending on the result of the monitoring.

In this example, considering that you defined a `running` tag when you start the
job in `Scrapy Cloud`_, if the job passes without errors, it will remove this tag.
If the job fails the `failed` tag will be added to the job so you can easily look
for failed jobs.

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.jobs.tags import AddJobTags, RemoveJobTags

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_passed_actions = [
            RemoveJobTags,
        ]

        monitors_failed_actions = [
            AddJobTags,
        ]

.. code-block:: python

    # settings.py
    SPIDERMON_JOB_TAGS_TO_ADD = ['failed', ]
    SPIDERMON_JOB_TAGS_TO_REMOVE = ['running', ]

By default we have the following settings when using these two actions:

SPIDERMON_JOB_TAGS_TO_ADD
-------------------------

List of tags to be included when `AddJobTags` is executed.

SPIDERMON_JOB_TAGS_TO_REMOVE
----------------------------

List of tags to be removed when `RemoveJobTags` is executed.

If you want to have different rules adding or removing tags for different results
of the monitoring, you need to create a custom action class including the name
of the setting that will contain the list of tags that will be included in the job:

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.jobs.tags import AddJobTags

    class AddJobTagsPassed(AddJobTags):
        tag_settings = 'TAG_TO_ADD_WHEN_PASS'

    class AddJobTagsFailed(AddJobTags):
        tag_settings = 'TAG_TO_ADD_WHEN_FAIL'

    class DummyMonitorSuite(MonitorSuite):
        monitors = [
            DummyMonitor,
        ]

        monitors_passed_actions = [
            AddJobTagsPassed,
        ]

        monitors_failed_actions = [
            AddJobTagsFailed,
        ]

.. code-block:: python

    # settings.py
    TAG_TO_ADD_WHEN_PASS = ['passed', ]
    TAG_TO_ADD_WHEN_FAIL = ['failed', ]

.. _Scrapy Cloud: https://zyte.com/scrapy-cloud