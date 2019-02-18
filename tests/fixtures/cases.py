from __future__ import absolute_import
from spidermon import Monitor


class EmptyMonitor(Monitor):
    pass


class Monitor01(Monitor):
    def test_a(self):
        pass

    def test_b(self):
        pass

    def test_c(self):
        pass


class Monitor02(Monitor):
    def test_d(self):
        pass

    def test_e(self):
        pass
