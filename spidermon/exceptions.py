class SpidermonException(Exception):
    pass


class InvalidStatsOperation(SpidermonException):
    pass


class NotAllowedMethod(SpidermonException):
    pass


class InvalidMonitor(SpidermonException):
    pass


class InvalidMonitorIterable(InvalidMonitor):
    pass


class InvalidMonitorClass(InvalidMonitor):
    pass


class InvalidMonitorTuple(InvalidMonitor):
    pass


class InvalidExpression(SpidermonException):
    pass


class InvalidResult(SpidermonException):
    pass


class SkipAction(SpidermonException):
    pass
