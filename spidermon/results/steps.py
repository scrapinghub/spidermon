from collections import OrderedDict
import time

from spidermon import settings

from .items import ItemResult, TestResult, ActionResult


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
    def successful(self):
        for result in self._results.values():
            if result.status not in self.successful_statuses:
                return False
        return True

    @property
    def number_of_items(self):
        return len(self._results)

    def add_item(self, item):
        self._results[item] = self.item_result_class(item)

    def start(self):
        #print 'starting step', self.name
        self.start_time = time.time()

    def finish(self):
        self.finish_time = time.time()

    def items_for_status(self, status):
        return [result for item, result in self._results.items()
                if result.status == status]

    @property
    def all_items(self):
        return self._results.values()

    def get_infos(self):
        raise NotImplementedError

    def __getitem__(self, key):
        return self._results[key]


class TestsStep(Step):
    item_result_class = TestResult
    successful_statuses = settings.TESTS_SUCCESSFUL_STATUSES
    error_statuses = settings.TESTS_ERROR_STATUSES

    def get_infos(self):
        return {
            'failures': len(self.items_for_status(settings.TEST_STATUS_FAILURE)),
            'errors': len(self.items_for_status(settings.TEST_STATUS_ERROR)),
            'skipped': len(self.items_for_status(settings.TEST_STATUS_SKIPPED)),
            'expected failures': len(self.items_for_status(settings.TEST_STATUS_EXPECTED_FAILURE)),
            'unexpected successes': len(self.items_for_status(settings.TEST_STATUS_UNEXPECTED_SUCCESS)),
        }


class ActionsStep(Step):
    item_result_class = ActionResult
    successful_statuses = settings.ACTIONS_SUCCESSFUL_STATUSES
    error_statuses = settings.ACTIONS_ERROR_STATUSES

    def get_infos(self):
        return {
            'errors': len(self.items_for_status(settings.ACTION_STATUS_ERROR)),
            'skipped': len(self.items_for_status(settings.ACTION_STATUS_SKIPPED)),
        }
