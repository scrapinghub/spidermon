import pytest

from spidermon.monitors import Monitor


class MonitorWithoutTests(Monitor):
    pass


class Monitor01(Monitor):
    @pytest.mark.skip
    def test_a(self):
        pass

    def test_b(self):
        pass

    def test_c(self):
        pass

