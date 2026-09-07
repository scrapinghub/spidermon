import pytest

pytest.importorskip("scrapy")

from spidermon.contrib.actions.reports.s3 import CreateS3Report, S3Uploader
from spidermon.exceptions import NotConfigured


@pytest.fixture
def boto3_client(mocker):
    return mocker.patch("spidermon.contrib.actions.reports.s3.boto3.client")


def test_uploader_uses_boto3_client(boto3_client):
    S3Uploader("ACCESS_KEY", "SECRET_KEY")
    boto3_client.assert_called_once_with(
        "s3",
        aws_access_key_id="ACCESS_KEY",
        aws_secret_access_key="SECRET_KEY",
    )


def test_upload_from_content(boto3_client):
    uploader = S3Uploader("ACCESS_KEY", "SECRET_KEY")
    uploader.upload_from_content(
        content="report content",
        s3_bucket="my-bucket",
        s3_filename="report.html",
        headers={"Content-Type": "text/html"},
        make_public=True,
    )
    boto3_client.return_value.put_object.assert_called_once_with(
        Bucket="my-bucket",
        Key="report.html",
        Body=b"report content",
        ContentType="text/html",
        ACL="public-read",
    )


def test_upload_from_file(boto3_client, tmp_path):
    source_file = tmp_path / "report.html"
    source_file.write_text("report content")
    uploaded_body = []
    boto3_client.return_value.put_object.side_effect = lambda **kwargs: (
        uploaded_body.append(kwargs["Body"].read())
    )

    uploader = S3Uploader("ACCESS_KEY", "SECRET_KEY")
    uploader.upload_from_file(
        source_filename=source_file,
        s3_bucket="my-bucket",
        s3_filename="report.html",
    )

    kwargs = boto3_client.return_value.put_object.call_args.kwargs
    assert kwargs["Bucket"] == "my-bucket"
    assert kwargs["Key"] == "report.html"
    assert uploaded_body == [b"report content"]
    assert "ACL" not in kwargs


def test_fail_if_no_aws_access_key():
    with pytest.raises(NotConfigured):
        CreateS3Report(
            template="report.jinja",
            aws_secret_key="SECRET_KEY",
            s3_bucket="my-bucket",
            s3_filename="report.html",
        )


def test_fail_if_no_aws_secret_key():
    with pytest.raises(NotConfigured):
        CreateS3Report(
            template="report.jinja",
            aws_access_key="ACCESS_KEY",
            s3_bucket="my-bucket",
            s3_filename="report.html",
        )


def test_fail_if_no_s3_bucket():
    with pytest.raises(NotConfigured):
        CreateS3Report(
            template="report.jinja",
            aws_access_key="ACCESS_KEY",
            aws_secret_key="SECRET_KEY",
            s3_filename="report.html",
        )


def test_fail_if_no_s3_filename():
    with pytest.raises(NotConfigured):
        CreateS3Report(
            template="report.jinja",
            aws_access_key="ACCESS_KEY",
            aws_secret_key="SECRET_KEY",
            s3_bucket="my-bucket",
        )


def test_after_render_report_uploads_to_s3(boto3_client, mocker):
    report = CreateS3Report(
        template="report.jinja",
        aws_access_key="ACCESS_KEY",
        aws_secret_key="SECRET_KEY",
        s3_bucket="my-bucket",
        s3_filename="report.html",
        make_public=True,
    )
    report.report = "rendered report"
    report.result = mocker.MagicMock()
    report.after_render_report()

    kwargs = boto3_client.return_value.put_object.call_args.kwargs
    assert kwargs["Bucket"] == "my-bucket"
    assert kwargs["Key"] == report.get_s3_filename()
    assert kwargs["Body"] == b"rendered report"
    assert kwargs["ContentType"] == "text/html"
    assert kwargs["ACL"] == "public-read"


def test_get_s3_report_url(mocker):
    report = CreateS3Report(
        template="report.jinja",
        aws_access_key="ACCESS_KEY",
        aws_secret_key="SECRET_KEY",
        s3_bucket="my-bucket",
        s3_filename="report.html",
    )
    report.result = mocker.MagicMock()
    url = report.get_s3_report_url()
    assert url.startswith("https://s3.amazonaws.com/my-bucket/reports/")
    assert url.endswith("/report.html")
