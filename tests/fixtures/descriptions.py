from __future__ import absolute_import
from spidermon import Monitor, MonitorSuite, monitors


# ----------------------------------
# Monitors
# ----------------------------------
class BaseMonitor(Monitor):
    def runTest(self):
        pass


class NotDescriptedMonitor(BaseMonitor):
    pass


class DocstringDescriptedMonitor(BaseMonitor):
    """docstring monitor description"""

    pass


@monitors.description("decorator monitor description")
class DescoratedDescriptedMonitor(BaseMonitor):
    pass


@monitors.description("decorator monitor description")
class DescoratedDescriptedMonitor2(BaseMonitor):
    """docstring monitor description"""


# ----------------------------------
# Suites
# ----------------------------------
class NotDescriptedSuite(MonitorSuite):
    pass


class DocstringDescriptedSuite(MonitorSuite):
    """docstring suite description"""

    pass


@monitors.description("decorator suite description")
class DescoratedDescriptedSuite(MonitorSuite):
    pass


@monitors.description("decorator suite description")
class DescoratedDescriptedSuite2(MonitorSuite):
    """docstring suite description"""


# ----------------------------------
# Methods
# ----------------------------------
class DescriptedMethodsMonitor(Monitor):
    def test_not_descripted(self):
        pass

    def test_docstring_descripted(self):
        """docstring method description"""
        pass

    @monitors.description("decorator method description")
    def test_decorator_descripted(self):
        pass

    @monitors.description("decorator method description")
    def test_decorator_descripted2(self):
        """docstring method description"""
