from spidermon.rules import Rule, TestCase
from spidermon import settings


class ATestCase(TestCase):
    def test_method_a(self):
        return self.stats.item_scraped_count > 100

    def test_method_b(self):
        return self.stats.item_scraped_count > 100


class DummyRule(Rule):
    def check(self, stats):
        return True


class SimpleRule(Rule):
    def check(self, stats):
        return stats.item_scraped_count > 100


def a_function(stats):
    return stats.item_scraped_count > 100

lambda_expression = lambda stats: stats.item_scraped_count > 100
python_expression = 'stats.item_scraped_count > 100'

RULE_OBJECT_BASE = Rule()
RULE_OBJECT_DUMMY = DummyRule()
RULE_OBJECT_SIMPLE = SimpleRule()
RULE_EXPRESSION = python_expression
RULE_LAMBDA = lambda_expression
RULE_FUNCTION = a_function
RULE_TESTCASE = ATestCase()


RULES = [
    RULE_OBJECT_SIMPLE,
    RULE_EXPRESSION,
    RULE_LAMBDA,
    RULE_FUNCTION,
    RULE_TESTCASE,
]

RULES_AS_TUPLE2 = [
    ('RULE_OBJECT', RULE_OBJECT_SIMPLE),
    ('RULE_EXPRESSION', RULE_EXPRESSION),
    ('RULE_LAMBDA', RULE_LAMBDA),
    ('RULE_FUNCTION', RULE_FUNCTION),
    ('RULE_TESTCASE', RULE_TESTCASE),
]

RULES_AS_TUPLE3 = [
    ('RULE_OBJECT', RULE_OBJECT_SIMPLE, settings.LEVEL_HIGH),
    ('RULE_EXPRESSION', RULE_EXPRESSION, settings.LEVEL_HIGH),
    ('RULE_LAMBDA', RULE_LAMBDA, settings.LEVEL_HIGH),
    ('RULE_FUNCTION', RULE_FUNCTION, settings.LEVEL_HIGH),
    ('RULE_TESTCASE', RULE_TESTCASE, settings.LEVEL_HIGH),
]