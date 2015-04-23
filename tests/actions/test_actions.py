import pytest

from spidermon import Action


def test_base_action():
    with pytest.raises(NotImplementedError):
        Action().run(None)
