from __future__ import absolute_import
from collections import OrderedDict
import time
from six import itervalues

from spidermon import settings

from .items import ItemResult, MonitorResult, ActionResult


class Step(object):
    item_result_class = ItemResult
    successful_statuses = []
    error_statuses = []

    def __init__(self, name):
        self.name = name
        self._results = OrderedDict()
        self.start_time = 0
        self.finish_time = 0

    @property
    def time_taken(self):
        return self.finish_time - self.start_time

    @property
    def number_of_items(self):
        return len(self._results)

    def add_item(self, item):
        result = self.item_result_class(item)
        self._results[item] = result
        return result

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.finish_time = time.time()

    def items_for_status(self, status):
        return [
            result for item, result in self._results.items() if result.status == status
        ]

    def items_for_statuses(self, statuses):
        items = []
        for status in statuses:
            items += self.items_for_status(status)
        return items

    @property
    def all_items(self):
        return list(itervalues(self._results))

    def get_infos(self):
        raise NotImplementedError

    def __getitem__(self, key):
        return self._results[key]

    @property
    def successful_results(self):
        results = []
        for successful_status in self.successful_statuses:
            results += self.items_for_status(successful_status)
        return results

    @property
    def error_results(self):
        results = []
        for error_status in self.error_statuses:
            results += self.items_for_status(error_status)
        return results

    @property
    def successful(self):
        return not self.has_errors

    @property
    def has_errors(self):
        return len(self.error_results) > 0


class MonitorStep(Step):
    item_result_class = MonitorResult
    successful_statuses = settings.MONITOR.STATUSES.SUCCESSFUL
    error_statuses = settings.MONITOR.STATUSES.ERROR

    def get_infos(self):
        return {
            "failures": len(self.items_for_status(settings.MONITOR.STATUS.FAILURE)),
            "errors": len(self.items_for_status(settings.MONITOR.STATUS.ERROR)),
            "skipped": len(self.items_for_status(settings.MONITOR.STATUS.SKIPPED)),
            "expected failures": len(
                self.items_for_status(settings.MONITOR.STATUS.EXPECTED_FAILURE)
            ),
            "unexpected successes": len(
                self.items_for_status(settings.MONITOR.STATUS.UNEXPECTED_SUCCESS)
            ),
        }


class ActionsStep(Step):
    item_result_class = ActionResult
    successful_statuses = settings.ACTION.STATUSES.SUCCESSFUL
    error_statuses = settings.ACTION.STATUSES.ERROR

    def get_infos(self):
        return {
            "errors": len(self.items_for_status(settings.ACTION.STATUS.ERROR)),
            "skipped": len(self.items_for_status(settings.ACTION.STATUS.SKIPPED)),
        }
