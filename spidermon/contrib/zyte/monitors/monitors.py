import json
import math
import os

from spidermon import monitors
from spidermon.contrib.scrapy.monitors.base import BaseStatMonitor
from spidermon.contrib.zyte.utils import Client
from spidermon.exceptions import NotConfigured

SPIDERMON_JOBS_COMPARISON = "SPIDERMON_JOBS_COMPARISON"
SPIDERMON_JOBS_COMPARISON_STATES = "SPIDERMON_JOBS_COMPARISON_STATES"
SPIDERMON_JOBS_COMPARISON_TAGS = "SPIDERMON_JOBS_COMPARISON_TAGS"
SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS = "SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS"
SPIDERMON_JOBS_COMPARISON_THRESHOLD = "SPIDERMON_JOBS_COMPARISON_THRESHOLD"
SPIDERMON_JOBS_COMPARISON_ARGUMENTS = "SPIDERMON_JOBS_COMPARISON_ARGUMENTS"
SPIDERMON_JOBS_COMPARISON_ARGUMENTS_ENABLED = (
    "SPIDERMON_JOBS_COMPARISON_ARGUMENTS_ENABLED"
)


@monitors.name("Jobs Comparison Monitor")
class ZyteJobsComparisonMonitor(BaseStatMonitor):
    """
    .. note::
       This monitor is useful when running jobs in
       `Zyte's Scrapy Cloud <https://www.zyte.com/scrapy-cloud/>`_.

    Check for a drop in scraped item count compared to previous jobs.

    You need to set the number of previous jobs to compare, using ``SPIDERMON_JOBS_COMPARISON``.
    The default is ``0`` which disables the monitor. We use the average of the scraped items count.

    You can configure which percentage of the previous item count is the minimum acceptable, by
    using the setting ``SPIDERMON_JOBS_COMPARISON_THRESHOLD``. We expect a float number between
    ``0.0`` (not inclusive) and with no upper limit (meaning we can check if itemcount is increasing
    at a certain rate). If not set, a NotConfigured error will be raised.

    You can filter which jobs to compare based on their states using the
    ``SPIDERMON_JOBS_COMPARISON_STATES`` setting. The default value is ``("finished",)``.

    You can also filter which jobs to compare based on their tags using the
    ``SPIDERMON_JOBS_COMPARISON_TAGS`` setting. Among the defined tags we consider only those
    that are also present in the current job.

    You can also filter which jobs to compare based on their close reason using the
    ``SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS`` setting. The default value is ``()``,
    which doesn't filter any job based on close_reason. To only consider successfully finished jobs,
    use ``("finished", ) instead.``

    You can also filter which jobs to compare based on the job arguments using the
    ``SPIDERMON_JOBS_COMPARISON_ARGUMENTS`` setting. It will filter any job based on spider_args.
    The job that will have all the desired arguments will be processed.
    Example {"debug_url": "https://www.google.com"} or {"is_full_crawl": True}
    You can enable this filter by setting SPIDERMON_JOBS_COMPARISON_ARGUMENTS_ENABLED as True in the settings.
    Otherwise, this filter will not be applied
    """

    stat_name = "item_scraped_count"
    assert_type = ">="

    def run(self, result):
        if (
            SPIDERMON_JOBS_COMPARISON not in self.crawler.settings.attributes
            or self.crawler.settings.getint(SPIDERMON_JOBS_COMPARISON) <= 0
        ):
            raise NotConfigured(
                f"Configure SPIDERMON_JOBS_COMPARISON to your project "
                f"settings to use {self.monitor_name}.",
            )

        if (
            SPIDERMON_JOBS_COMPARISON_THRESHOLD not in self.crawler.settings.attributes
            or self.crawler.settings.getfloat(SPIDERMON_JOBS_COMPARISON_THRESHOLD) <= 0
        ):
            raise NotConfigured(
                f"Configure SPIDERMON_JOBS_COMPARISON_THRESHOLD to your project "
                f"settings to use {self.monitor_name}.",
            )

        return super().run(result)

    def _get_jobs(self, states, number_of_jobs):
        tags = self._get_tags_to_filter()
        close_reasons = self.crawler.settings.getlist(
            SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS,
            (),
        )
        args = self._get_args_to_filter()
        args_enabled = self.crawler.settings.getbool(
            SPIDERMON_JOBS_COMPARISON_ARGUMENTS_ENABLED,
            False,
        )

        total_jobs = []
        start = 0
        client = Client(self.crawler.settings)
        MAX_API_COUNT = 1000

        while True:
            # API has a 1000 results limit
            count = min(number_of_jobs - len(total_jobs), MAX_API_COUNT)
            current_jobs = client.spider.jobs.list(
                start=start,
                state=states,
                count=count,
                has_tag=tags or None,
            )

            for job in current_jobs:
                if close_reasons and job.get("close_reason") not in close_reasons:
                    continue

                if args_enabled and not self._has_desired_args(job, args):
                    continue

                total_jobs.append(job)

            if len(current_jobs) < MAX_API_COUNT or len(total_jobs) >= number_of_jobs:
                # Stop paginating if results are less than 1000 (pagination not required)
                # or target jobs was reached - no more pagination required
                break

            start += len(current_jobs)

        return total_jobs

    def _get_tags_to_filter(self):
        """
        Return a list of tags with the intersection of the desired tags to filter and
        the ones from the current job.
        """
        desired_tags = self.crawler.settings.getlist(SPIDERMON_JOBS_COMPARISON_TAGS)
        if not desired_tags:
            return []

        current_tags = json.loads(os.environ.get("SHUB_JOB_DATA", "{}")).get("tags")
        if not current_tags:
            return []

        tags_to_filter = set(desired_tags) & set(current_tags)
        return sorted(tags_to_filter)

    def _get_args_to_filter(self):
        """Return a list of desired arguments to filter."""
        desired_args = self.crawler.settings.getdict(
            SPIDERMON_JOBS_COMPARISON_ARGUMENTS,
        )
        if not desired_args:
            return {}

        return desired_args

    def _has_desired_args(self, job, args):
        if not args and not job.get("spider_args"):
            return True
        if not args and job.get("spider_args"):
            return False

        job_args = job["spider_args"].keys()
        if not all(a in job_args for a in args):
            return False

        return args == job["spider_args"]

    def get_threshold(self):
        number_of_jobs = self.crawler.settings.getint(SPIDERMON_JOBS_COMPARISON)

        threshold = self.crawler.settings.getfloat(SPIDERMON_JOBS_COMPARISON_THRESHOLD)

        states = self.crawler.settings.getlist(
            SPIDERMON_JOBS_COMPARISON_STATES,
            ("finished",),
        )

        jobs = self._get_jobs(states, number_of_jobs)

        previous_count = sum(job.get("items", 0) for job in jobs) / len(jobs)

        return math.ceil(previous_count * threshold)
