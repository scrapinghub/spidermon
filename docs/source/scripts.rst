==============
Helper scripts
==============

Checking failed jobs
--------------------

There are cases where jobs can fail abruptly in such a way that Spidermon 
(or any other extensions that run at the end of Scrapy) won't run.

In these situations, we won't be alerted that something happened because 
Spidermon didn't run at the end, so it won't generate alerts and ScrapyCloud 
also won't warn about them.

This script has the objective of helping identifying those jobs.

In order to use it (either locally or in scrapy cloud), put the following field
in your project:

    .. code-block:: python

        from spidermon.scripts.check_failed_jobs import CheckFailedJobs

        with CheckFailedJobs() as checker:
            checker.run()

Then you can call you new file and pass in the arguments: scrapy cloud API key, project id and
the lookback (how many hours in the past to look for failed jobs).

The script should report as errors any jobs that have the 'failed' as a close reason.

If you want to run it in scrapy cloud, don't forget to include the script in your
`setup.py` file, so it gets picked up and deployed.