from scrapy.settings import Settings

from spidermon.utils.settings import get_aws_credentials


def test_spidermon_aws_credentials_not_set():
    settings = Settings()

    (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(settings)

    assert aws_access_key_id is None
    assert aws_secret_access_key is None


def test_spidermon_aws_credentials(mocker):
    warn_mock = mocker.patch("spidermon.utils.settings.warnings.warn")
    settings = Settings(
        {
            "SPIDERMON_AWS_ACCESS_KEY": "aws_access_key",
            "SPIDERMON_AWS_SECRET_KEY": "aws_secret_key",
        }
    )

    (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(settings)

    assert aws_access_key_id == "aws_access_key"
    assert aws_secret_access_key == "aws_secret_key"
    warn_mock.assert_called_with(mocker.ANY, DeprecationWarning)


def test_spidermon_aws_credentials_scrapy_like():
    settings = Settings(
        {
            "SPIDERMON_AWS_ACCESS_KEY_ID": "aws_access_key_id",
            "SPIDERMON_AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
        }
    )

    (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(settings)

    assert aws_access_key_id == "aws_access_key_id"
    assert aws_secret_access_key == "aws_secret_access_key"


def test_spidermon_aws_credentials_fall_back_to_scrapy():
    settings = Settings(
        {
            "AWS_ACCESS_KEY_ID": "scrapy_aws_access_key_id",
            "AWS_SECRET_ACCESS_KEY": "scrapy_aws_secret_access_key",
        }
    )

    (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(settings)

    assert aws_access_key_id == "scrapy_aws_access_key_id"
    assert aws_secret_access_key == "scrapy_aws_secret_access_key"


def test_spidermon_aws_credentials_are_preferred_over_scrapy_ones():
    settings = Settings(
        {
            "AWS_ACCESS_KEY_ID": "scrapy_aws_access_key_id",
            "AWS_SECRET_ACCESS_KEY": "scrapy_aws_secret_access_key",
            "SPIDERMON_AWS_ACCESS_KEY_ID": "spidermon_aws_access_key_id",
            "SPIDERMON_AWS_SECRET_ACCESS_KEY": "spidermon_aws_secret_access_key",
        }
    )

    (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(settings)

    assert aws_access_key_id == "spidermon_aws_access_key_id"
    assert aws_secret_access_key == "spidermon_aws_secret_access_key"


def test_spidermon_old_aws_credentials_are_preferred_over_new_ones(mocker):
    mocker.patch(
        "spidermon.utils.settings.warnings.warn"
    )  # avoid the warning in the tests
    settings = Settings(
        {
            "SPIDERMON_AWS_ACCESS_KEY": "old_aws_access_key",
            "SPIDERMON_AWS_SECRET_KEY": "old_aws_secret_key",
            "SPIDERMON_AWS_ACCESS_KEY_ID": "new_aws_access_key_id",
            "SPIDERMON_AWS_SECRET_ACCESS_KEY": "new_aws_secret_access_key",
        }
    )

    (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(settings)

    assert aws_access_key_id == "old_aws_access_key"
    assert aws_secret_access_key == "old_aws_secret_key"
