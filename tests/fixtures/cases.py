from spidermon import Monitor


class EmptyMonitor(Monitor):
    pass


class Monitor01(Monitor):
    def test_a(self) -> None:
        pass

    def test_b(self) -> None:
        pass

    def test_c(self) -> None:
        pass


class Monitor02(Monitor):
    def test_d(self) -> None:
        pass

    def test_e(self) -> None:
        pass
