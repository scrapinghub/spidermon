class SpiderMonException(Exception):
    pass


class InvalidStatsOperation(SpiderMonException):
    pass


class NotAllowedMethod(SpiderMonException):
    pass


class InvalidMonitor(SpiderMonException):
    pass


class InvalidMonitorIterable(InvalidMonitor):
    pass


class InvalidMonitorClass(InvalidMonitor):
    pass


class InvalidMonitorTuple(InvalidMonitor):
    pass
