from unittest import mock

import pytest
from scrapy.utils.test import get_crawler
from spidermon.utils import zyte


@pytest.fixture
def no_env_mock_module(monkeypatch):
    monkeypatch.delenv("SHUB_JOBKEY", raising=False)
    monkeypatch.setattr(zyte, "ScrapinghubClient", mock.MagicMock())
    return zyte


@pytest.fixture
def mock_module(monkeypatch):
    monkeypatch.setenv("SHUB_JOBKEY", "123/456/789")
    monkeypatch.setenv("SH_APIKEY", "foobar")
    monkeypatch.setattr(zyte, "ScrapinghubClient", mock.MagicMock())
    return zyte


@pytest.fixture
def settings():
    return get_crawler().settings


def test_client_creation_no_env(no_env_mock_module, settings):
    client = no_env_mock_module.Client(settings)
    assert client.available is False
    assert client.project_id is None
    assert client.spider_id is None
    assert client.job_id is None

    with pytest.raises(RuntimeError):
        client._apikey()


def test_client_creation(mock_module, settings):
    client = mock_module.Client(settings)
    assert client.available
    assert client.project_id == 123
    assert client.spider_id == 456
    assert client.job_id == 789


def test_client_property_project(mock_module, settings):
    client = mock_module.Client(settings)

    assert client._project is None
    client.project
    assert client._project is not None
    client._client.get_project.assert_called_with("123")


def test_client_property_job(mock_module, settings):
    client = mock_module.Client(settings)

    assert client._job is None
    client.job
    assert client._job is not None
    client._client.get_job.assert_called_with("123/456/789")


def test_client_property_spider(mock_module, settings):
    client = mock_module.Client(settings)
    client._job = mock.Mock()
    client._job.metadata.get.return_value = "my_awesome_spider"

    assert client._spider is None
    client.spider
    assert client._project is not None
    assert client._job is not None
    assert client._spider is not None

    client._job.metadata.get.assert_called_with("spider")
    client._project.spiders.get.assert_called_with("my_awesome_spider")


def test_client_close(mock_module, settings):
    client = mock_module.Client(settings)

    client.client
    client.close()
    client._client.close.assert_called()


@pytest.mark.parametrize("expected", [False, True])
def test_has_client(monkeypatch, expected):
    import sys
    from importlib import reload

    if not expected:
        monkeypatch.setitem(sys.modules, "scrapinghub", None)

    reload(zyte)
    assert zyte.HAS_CLIENT == expected


def test_client_settings_priority(mock_module, monkeypatch):
    shub_apikey = "SHUB_APIKEY"
    shub_jobauth = "SHUB_JOBAUTH"
    monkeypatch.setenv("SHUB_JOBAUTH", shub_jobauth)

    # Crawler settings has top priority
    settings = get_crawler(settings_dict={"SHUB_APIKEY": shub_apikey}).settings
    client = mock_module.Client(settings)
    assert client._apikey() == shub_apikey

    # then, SH_APIKEY
    empty_settings = get_crawler().settings
    client = mock_module.Client(empty_settings)
    assert client._apikey() == "foobar"

    # then,  SHUB_JOBAUTH
    monkeypatch.delenv("SH_APIKEY")
    assert client._apikey() == shub_jobauth

    # Otherwise, raise runtime error
    monkeypatch.delenv("SHUB_JOBAUTH")
    client = mock_module.Client(empty_settings)
    with pytest.raises(RuntimeError):
        client._apikey()
