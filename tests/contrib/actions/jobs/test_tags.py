from unittest.mock import MagicMock, patch

import pytest
from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.jobs.tags import AddJobTags, JobTagsAction, RemoveJobTags
from spidermon.exceptions import NotConfigured


@pytest.fixture
def test_settings():
    return {
        "SPIDERMON_JOB_TAGS_TO_ADD": ["add_foo", "add_bar"],
        "SPIDERMON_JOB_TAGS_TO_REMOVE": ["remove_foo", "remove_bar"],
    }


class SettableDict(dict):
    def set(self, key, value):
        self[key] = value


def test_run_action(test_settings):
    crawler = get_crawler(settings_dict=test_settings)
    job_tags_action = JobTagsAction.from_crawler(crawler)

    job_tags_action.tags = MagicMock(return_value=["foo", "bar"])
    job_tags_action.data = MagicMock()
    job_tags_action.data.job = None
    with pytest.raises(NotConfigured):
        job_tags_action.run_action()

    job_tags_action.data.job = MagicMock()
    with pytest.raises(NotImplementedError):
        job_tags_action.run_action()


def test_add_job_tags(test_settings):
    crawler = get_crawler(settings_dict=test_settings)
    add_job_tags = AddJobTags.from_crawler(crawler)

    assert add_job_tags.tags == ["add_foo", "add_bar"]

    add_job_tags.data = MagicMock()
    add_job_tags.data.job.metadata = SettableDict({"tags": []})
    add_job_tags.run_action()
    assert add_job_tags.data.job.metadata.get("tags") == ["add_foo", "add_bar"]


def test_remove_job_tags(test_settings):
    crawler = get_crawler(settings_dict=test_settings)
    remove_job_tags = RemoveJobTags.from_crawler(crawler)

    assert remove_job_tags.tags == ["remove_foo", "remove_bar"]

    remove_job_tags.data = MagicMock()
    remove_job_tags.data.job.metadata = SettableDict(
        {"tags": ["remove_foo", "remove_bar"]}
    )
    remove_job_tags.run_action()
    assert remove_job_tags.data.job.metadata.get("tags") == []
