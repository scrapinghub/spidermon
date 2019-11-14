try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
import pytest
from unittest import TestCase

from spidermon.contrib.actions.jobs.tags import JobTagsAction, AddJobTags, RemoveJobTags
from spidermon.exceptions import NotConfigured

TAG = "custom_tag"


@pytest.mark.parametrize(
    "tags, expected_tags", [(None, []), ([TAG], [TAG]), (TAG, [TAG])],
)
def test_job_tags_action_init(tags, expected_tags):
    job_tags = JobTagsAction(tags)
    assert job_tags.tags == expected_tags


class JobTagsActionTests(TestCase):
    def test_run_action_without_data(self):
        job_tags = JobTagsAction(TAG)
        with pytest.raises(AttributeError):
            job_tags.run_action()

    def test_run_action_without_data_job(self):
        job_tags = JobTagsAction(TAG)
        job_tags.data = MagicMock()
        job_tags.data.job = ""
        with pytest.raises(NotConfigured) as e:
            job_tags.run_action()
        assert "Job not available!" in str(e.value)

    def test_run_action(self):
        job_tags = JobTagsAction(TAG)
        job_tags.data = MagicMock()
        metadata = MagicMock()
        job_tags.data.job.metadata = metadata
        job_tags.process_tags = MagicMock()
        job_tags.run_action()
        job_tags.process_tags.assert_called_once_with(metadata)
        job_tags.data.job.metadata.save.assert_called_once_with()


def test_add_job_tags_properties():
    job_tags = AddJobTags(TAG)
    assert job_tags.tag_settings == "SPIDERMON_JOB_TAGS_TO_ADD"


class AddJobTagsTests(TestCase):
    def test_process_tags(self):
        metadata = {"tags": []}
        job_tags = AddJobTags(TAG)
        job_tags.process_tags(metadata)
        assert TAG in metadata["tags"]


def test_remove_job_tags_properties():
    job_tags = RemoveJobTags(TAG)
    assert job_tags.tag_settings == "SPIDERMON_JOB_TAGS_TO_REMOVE"


class RemoveJobTagsTests(TestCase):
    def test_process_tags(self):
        metadata = {"tags": [TAG]}
        job_tags = RemoveJobTags(TAG)
        job_tags.process_tags(metadata)
        assert TAG not in metadata["tags"]
