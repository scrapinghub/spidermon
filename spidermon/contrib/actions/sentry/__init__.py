from __future__ import absolute_import

import logging

from slugify import slugify

logger = logging.getLogger(__name__)

from sentry_sdk import configure_scope
from sentry_sdk.client import Client

from spidermon import Action
from spidermon.exceptions import NotConfigured


class SendSentryMessage(Action):
    sentry_dsn = None
    fake = False
    sentry_log_level = "error"
    project_name = ""
    environment = "Development"

    def __init__(
        self,
        sentry_dsn=None,
        fake=None,
        sentry_log_level=None,
        project_name="",
        environment="",
    ):
        super(SendSentryMessage, self).__init__()
        self.fake = fake or self.fake
        self.sentry_log_level = sentry_log_level or self.sentry_log_level
        self.sentry_dsn = sentry_dsn or self.sentry_dsn

        self.project_name = project_name or self.project_name
        self.environment = environment or self.environment

        if not self.fake and not self.sentry_dsn:
            raise NotConfigured("Missing SPIDERMON_SENTRY_DSN setting")

        if not self.project_name:
            raise NotConfigured("Missing SPIDERMON_SENTRY_PROJECT_NAME setting")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            "fake": crawler.settings.getbool("SPIDERMON_SENTRY_FAKE"),
            "sentry_dsn": crawler.settings.get("SPIDERMON_SENTRY_DSN"),
            "sentry_log_level": crawler.settings.get("SPIDERMON_SENTRY_LOG_LEVEL"),
            "project_name": crawler.settings.get("SPIDERMON_SENTRY_PROJECT_NAME"),
            "environment": crawler.settings.get("SPIDERMON_SENTRY_ENVIRONMENT_TYPE"),
        }

    def run_action(self):
        message = self.get_message()
        if self.fake:
            logger.info(message)
        else:
            self.send_message(message)

    def get_title(self):
        return (
            "{project_name} | {environment} | Spider {spider_name} notification".format(
                project_name=self.project_name,
                environment=self.environment,
                spider_name=self.data.spider.name,
            )
        )

    def get_message(self):
        """
        Returns message dictionary
        """
        message = dict()

        message["title"] = self.get_title()
        if self.data.job:
            message["job_link"] = "https://app.zyte.com/p/{job_id}".format(
                job_id=self.data.job.key
            )

        if self.data.spider:
            message["spider_name"] = self.data.spider.name

        if self.data.stats:
            message["items_count"] = self.data.stats.get("item_scraped_count", 0)

        if self.result:
            message["passed_monitors_count"] = len(self.result.monitors_passed_results)
            message["failed_monitors_count"] = len(self.result.monitors_failed_results)

            failed_monitors = []
            failure_reasons = []

            for result in self.result.monitors_failed_results:
                failed_monitors.append(result.monitor.name)
                failure_reasons.append(result.error)

            message["failure_reasons"] = "\n".join(failure_reasons)
            message["failed_monitors"] = failed_monitors

        return message

    def get_tags(self, message):
        tags = {
            "spider_name": message.get("spider_name", ""),
            "project_name": self.project_name,
        }
        for failed_monitor in message.get("failed_monitors", []):
            key = slugify(failed_monitor.split("/")[-1], max_length=32, separator="_")
            tags[key] = 1
        return tags

    def send_message(self, message):

        sentry_client = Client(dsn=self.sentry_dsn, environment=self.environment)

        with configure_scope() as scope:
            tags = self.get_tags(message)
            for key, val in tags.items():
                scope.set_tag(key, val)

            scope.set_extra("job_link", message.get("job_link", ""))
            scope.set_extra("spider_name", message.get("spider_name", ""))
            scope.set_extra("items_count", message.get("items_count", 0))

            scope.set_extra(
                "passed_monitors_count", message.get("passed_monitors_count", 0)
            )
            scope.set_extra(
                "failed_monitors_count", message.get("failed_monitors_count", 0)
            )

            scope.set_extra("failed_monitors", message.get("failed_monitors", []))

            sentry_client.capture_event(
                {
                    "message": "{title} \n {description}".format(
                        title=message.get("title"),
                        description=message.get("failure_reasons", ""),
                    ),
                    "level": self.sentry_log_level,
                },
                scope=scope,
            )
        logger.info("Notification sent to the sentry dashboard!!")

        sentry_client.close()
