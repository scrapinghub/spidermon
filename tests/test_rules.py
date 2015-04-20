import pytest
import unittest

from spidermon import Rule, CallableRule
from spidermon.context import create_context_dict


STATS_01 = {
    'scraped_items': 100,
}

STATS_02 = {
    'scraped_items': 0,
}

STATS_EMPTY = {}


class DummyRule(Rule):
    def check(self, stats):
        return True


class SimpleRule(Rule):
    def check(self, stats):
        return stats.scraped_items == 100


def function_rule(stats):
    return stats.scraped_items == 100


class RulesTest(unittest.TestCase):

    def setUp(self):
        self.context_stats_01 = create_context_dict(STATS_01)
        self.context_stats_02 = create_context_dict(STATS_02)
        self.context_stats_empty = create_context_dict(STATS_EMPTY)

    def test_base_rule(self):
        rule = Rule()
        with pytest.raises(NotImplementedError):
            rule.check(**self.context_stats_empty)

    def test_dummy_rule(self):
        rule = DummyRule()
        assert rule.check(**self.context_stats_empty) is True

    def test_simple_rule(self):
        rule = SimpleRule()
        assert rule.check(**self.context_stats_01) is True
        assert rule.check(**self.context_stats_02) is False
        with pytest.raises(AttributeError):
            rule.check(**self.context_stats_empty)

    def test_function_rule(self):
        rule = CallableRule(function_rule)
        assert rule.check(STATS_01) is True
        assert rule.check(STATS_02) is False
        with pytest.raises(AttributeError):
            rule.check(STATS_EMPTY)
