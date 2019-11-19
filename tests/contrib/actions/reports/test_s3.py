try:
    from unittest.mock import MagicMock, patch, mock_open
except ImportError:
    from mock import MagicMock, patch, mock_open
import pytest

from spidermon.contrib.actions.reports.s3 import S3Uploader, CreateS3Report
from spidermon.exceptions import NotConfigured

TEMPLATE = "template"
FILENAME = "filename"
DEFAULT_S3_CONTENT_TYPE = "text/html"
REPORT = "report"
AWS_KEY = "aws_key"
AWS_SECRET = "aws_secret"
S3_BUCKET = "S3_BUCKET"
S3_FILENAME = "filename"
SOURCE_FILENAME = "source_filename"
MAKE_PUBLIC = "make_public"
CONTENT = "content"
METHOD_NAME = "method_name"


@patch("spidermon.contrib.actions.reports.s3.S3Connection", return_value={})
def test_init(S3Connection):
    uploader = S3Uploader(AWS_KEY, AWS_SECRET)
    assert uploader.connection == {}
    S3Connection.assert_called_once_with(
        aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET
    )


@patch("spidermon.contrib.actions.reports.s3.open", new_callable=mock_open())
def test_upload_from_file(_open):
    uploader = S3Uploader(AWS_KEY, AWS_SECRET)
    uploader._upload_with_method = MagicMock()
    uploader.upload_from_file(SOURCE_FILENAME, S3_BUCKET, S3_FILENAME)
    _open.assert_called_once_with(SOURCE_FILENAME, "r")
    uploader._upload_with_method.assert_called_once_with(
        bucket=S3_BUCKET,
        method_name="set_contents_from_file",
        filename=S3_FILENAME,
        content=_open().__enter__(),
        headers=None,
        make_public=False,
    )


def test_upload_from_content():
    uploader = S3Uploader(AWS_KEY, AWS_SECRET)
    uploader._upload_with_method = MagicMock()
    uploader.upload_from_content(CONTENT, S3_BUCKET, S3_FILENAME)
    uploader._upload_with_method.assert_called_once_with(
        bucket=S3_BUCKET,
        method_name="set_contents_from_string",
        filename=S3_FILENAME,
        content=CONTENT,
        headers=None,
        make_public=False,
    )


@pytest.mark.parametrize("make_public", [(True), (False)])
@patch("spidermon.contrib.actions.reports.s3.Key")
def test_upload_with_method(Key, make_public):
    key = MagicMock()
    key.method_name = MagicMock()
    uploader = S3Uploader(AWS_KEY, AWS_SECRET)
    uploader.connection = MagicMock()
    uploader.connection.get_bucket.return_value = S3_BUCKET
    Key.return_value = key
    uploader._upload_with_method(
        S3_BUCKET, METHOD_NAME, S3_FILENAME, CONTENT, make_public=make_public
    )

    uploader.connection.get_bucket.assert_called_once_with(S3_BUCKET, validate=False)
    Key.assert_called_once_with(S3_BUCKET)
    assert key.key == S3_FILENAME
    key.method_name.assert_called_once_with(CONTENT, headers=None)
    if make_public:
        Key().make_public.assert_called_once_with()
    else:
        Key().make_public.assert_not_called()


@pytest.mark.parametrize(
    "kwargs, exception_message",
    [
        ({}, "You must define one template file."),
        ({"template": TEMPLATE}, "You must provide the AWS Access Key"),
        (
            {"template": TEMPLATE, "aws_access_key": AWS_KEY},
            "You must provide the AWS Secret Key",
        ),
        (
            {
                "template": TEMPLATE,
                "aws_access_key": AWS_KEY,
                "aws_secret_key": AWS_SECRET,
            },
            "You must define the s3 bucket.",
        ),
        (
            {
                "template": TEMPLATE,
                "aws_access_key": AWS_KEY,
                "aws_secret_key": AWS_SECRET,
                "s3_bucket": S3_BUCKET,
            },
            "You must define the s3 filename.",
        ),
    ],
)
def test_create_s3_report_init_exceptions(kwargs, exception_message):
    with pytest.raises(NotConfigured) as e:
        CreateS3Report(**kwargs)
    assert exception_message in str(e.value)


def test_create_s3_report_init_with_valid_data():
    CreateS3Report(
        template=TEMPLATE,
        aws_access_key=AWS_KEY,
        aws_secret_key=AWS_SECRET,
        s3_bucket=S3_BUCKET,
        s3_filename=S3_FILENAME,
    )


@pytest.fixture
def s3_report():
    report = CreateS3Report(
        template=TEMPLATE,
        aws_access_key=AWS_KEY,
        aws_secret_key=AWS_SECRET,
        s3_bucket=S3_BUCKET,
        s3_filename=S3_FILENAME,
        make_public=MAKE_PUBLIC,
    )
    report.report = REPORT
    report.data = MagicMock()
    return report


@patch("spidermon.contrib.actions.reports.s3.S3Uploader")
def test_s3_report_after_render_report(s3, s3_report):
    s3_report.get_s3_filename = MagicMock(return_value=S3_FILENAME)
    s3.upload_from_content = MagicMock()
    s3_report.after_render_report()
    s3().upload_from_content.assert_called_once_with(
        content=REPORT,
        s3_bucket=S3_BUCKET,
        s3_filename=s3_report.get_s3_filename(),
        headers={"Content-Type": DEFAULT_S3_CONTENT_TYPE},
        make_public=MAKE_PUBLIC,
    )


def test_get_s3_filename(s3_report):
    s3_report.get_url_secret = MagicMock(return_value="secret")
    s3_report.render_text_template = MagicMock(return_value="text template")
    s3_filename = s3_report.get_s3_filename()
    assert s3_filename == "reports/secret/text template"


def test_get_s3_report_url(s3_report):
    s3_report.s3_region_endpoint = "s3-region-endpoint"
    s3_report.get_s3_filename = MagicMock(return_value="s3-filename.pdf")
    get_s3_report_url = s3_report.get_s3_report_url()
    assert get_s3_report_url == "https://s3-region-endpoint/{}/s3-filename.pdf".format(
        S3_BUCKET
    )


@patch("spidermon.contrib.actions.reports.s3.URL_SECRET_KEY")
@patch("spidermon.contrib.actions.reports.s3.hashlib")
def test_get_url_secret_without_data_job(hashlib, URL_SECRET_KEY, s3_report):
    s3_report.data.job = ""
    hashlib.md5 = MagicMock()
    secret = s3_report.get_url_secret()
    hashlib.md5.assert_called_once_with(URL_SECRET_KEY.encode())
    hashlib.md5().hexdigest.assert_called_once_with()


@patch("spidermon.contrib.actions.reports.s3.URL_SECRET_KEY")
@patch("spidermon.contrib.actions.reports.s3.hashlib")
def test_get_url_secret_with_data_job(hashlib, URL_SECRET_KEY, s3_report):
    s3_report.data.job = MagicMock()
    s3_report.data.job.key = "1234/5/6"
    URL_SECRET_KEY += "6"
    hashlib.md5 = MagicMock()
    secret = s3_report.get_url_secret()
    hashlib.md5.assert_called_once_with(URL_SECRET_KEY.encode())
    hashlib.md5().hexdigest.assert_called_once_with()


def test_get_meta(s3_report):
    s3_report.get_s3_report_url = MagicMock(return_value="report_url")
    s3_report.data.meta = {"reports": []}
    meta = s3_report.get_meta()
    assert meta == {"reports_links": ["report_url"]}
