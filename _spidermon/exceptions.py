class SpiderMonException(Exception):
    pass


class InvalidRuleDefinition(SpiderMonException):
    pass


class InvalidRuleLevel(SpiderMonException):
    pass


class InvalidStatsOperation(SpiderMonException):
    pass


class InvalidExpression(SpiderMonException):
    pass


class InvalidCallable(SpiderMonException):
    pass


class InvalidTestCase(SpiderMonException):
    pass


class InvalidState(SpiderMonException):
    pass


class InvalidActionDefinition(SpiderMonException):
    pass