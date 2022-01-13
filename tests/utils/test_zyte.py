from unittest import mock

import pytest
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


def test_client_creation_no_env(no_env_mock_module):
    client = no_env_mock_module.Client()
    assert client.available == False
    assert client.project_id == None
    assert client.spider_id == None
    assert client.job_id == None


def test_client_creation(mock_module):
    client = mock_module.Client()
    assert client.available == True
    assert client.project_id == 123
    assert client.spider_id == 456
    assert client.job_id == 789


def test_client_property_project(mock_module):
    client = mock_module.Client()

    assert client._project == None
    client.project
    assert client._project != None
    client._client.get_project.assert_called_with("123")


def test_client_property_job(mock_module):
    client = mock_module.Client()

    assert client._job == None
    client.job
    assert client._job != None
    client._client.get_job.assert_called_with("123/456/789")


def test_client_property_spider(mock_module):
    client = mock_module.Client()
    client._job = mock.Mock()
    client._job.metadata.get.return_value = "my_awesome_spider"

    assert client._spider == None
    client.spider
    assert client._project != None
    assert client._job != None
    assert client._spider != None

    client._job.metadata.get.assert_called_with("spider")
    client._project.spiders.get.assert_called_with("my_awesome_spider")


def test_client_close(mock_module):
    client = mock_module.Client()

    client.client
    client.close()
    client._client.close.assert_called()
