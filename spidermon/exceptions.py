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